import multiprocessing.pool
import time
from dataclasses import dataclass
from queue import Queue
import logging
import os
import pandas as pd
from Shared.slope_api import SlopeApi
from typing import Any, Dict

@dataclass
class SigmaReportParams:
    workbook_id: str
    element_id: str
    filter_params: Dict[str, str]
    working_directory: str = r'C:\\Slope API'

    @staticmethod
    def from_dict(obj: Any) -> 'SigmaReportParams':
        _workbook = str(obj.get("workbook"))
        _element = str(obj.get("element"))
        _filters = obj.get("filters")
        return SigmaReportParams(_workbook, _element, _filters)

class SigmaReport:
    pool = multiprocessing.pool.ThreadPool()
    __filename: str = None
    __data: pd.DataFrame = None

    def __init__(self, api: SlopeApi, params: SigmaReportParams, filepath: str = None):
        self.api = api
        self.working_directory = params.working_directory + "\\Reports"
        self.workbook_id = params.workbook_id
        self.element_id = params.element_id
        self.filters = params.filter_params

        if filepath is not None:
            self.working_directory = filepath

        if not os.path.exists(self.working_directory):
            os.makedirs(self.working_directory)

    def __get_batch(self, filter_values: dict, results: Queue, batch_number: int = 1):
        report_params = self.__get_report_params(filter_values)

        filename = f'{self.working_directory}\\{self.workbook_id}_{self.element_id}_{batch_number}.csv'
        report_data = self.api.download_and_load_report(self.workbook_id, self.element_id, filename, 'Csv', report_params)
        results.put(report_data)

    def __get_report_params(self, filter_values: dict):
        report_params = {}
        for key, value in filter_values.items():
            sigma_id = self.filters.get(key)
            if sigma_id is not None:
                report_params[sigma_id] = value

        if "Projection-ID" not in report_params:
            report_params["Projection-ID"] = "0"

        return report_params

    def get_data(self) -> pd.DataFrame:
        if self.__data is None:
            if self.__filename is None:
                raise ValueError("Report data has not been retrieved yet. Call retrieve() or retrieve_batched() first.")
            else:
                self.__data = pd.read_csv(self.__filename, parse_dates=True)

        return self.__data
        
    def get_filename(self) -> str:  
        if self.__filename is None:
            raise ValueError("Report data has not been retrieved yet. Call retrieve() or retrieve_batched() first.")
        return self.__filename

    def retrieve(self, filter_values: dict) -> bool:
        self.__data = None
        report_params = self.__get_report_params(filter_values)

        self.__filename = f'{self.working_directory}\\{self.workbook_id}_{self.element_id}.csv'
        self.api.download_report(self.workbook_id, self.element_id, self.__filename, 'Csv', report_params)
        return True
    
    def retrieve_batched(self, batches: list[dict]) -> bool:

        report_tasks = []
        result_data = Queue()
        batch_number = 1
        for batch in batches:
            task = SigmaReport.pool.apply_async(self.__get_batch, args=(batch, result_data, batch_number))
            report_tasks.append(task)
            # space out api calls to prevent overloading
            time.sleep(5 / 1000)
            batch_number = batch_number + 1

        for task in report_tasks:
            task.wait()
            task.get()

        logging.debug(f"Combining Report Batches")
        results = result_data.get()
        while not result_data.empty():
            data = result_data.get()
            results = pd.concat([results, data])

        self.__data = results.drop_duplicates()
        self.__filename = f'{self.working_directory}\\{self.workbook_id}_{self.element_id}.csv'
        self.__data.to_csv(self.__filename, index=False, date_format='%m/%d/%Y', float_format='%g')

        #Clean Up Batches
        for i in range(batch_number):
            try:
                logging.debug(f"Deleting temp file '{self.working_directory}\\{self.workbook_id}_{self.element_id}_{i}.csv'")
                os.remove(f'{self.working_directory}\\{self.workbook_id}_{self.element_id}_{i}.csv')
            except OSError:
                pass

        return True