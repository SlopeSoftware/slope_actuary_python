from Shared.keys import api_key as key, api_secret as secret

# Substitute Real API credentials here
api_key = key
api_secret = secret

solver_folder = "C:\\Slope Api\\SBA Solver\\"     # Temporary folder on this computer for storing data

sba_scenario_generator = solver_folder + "SBA Scenario Generator.xlsx"

# Usage Notes
# The sba_template_name specified in this setting MUST have the following:
# 1. A single portfolio named 'Inforce Portfolio' (this can be changed by changing the projection update template below)
# 2. The proper reinvestment strategy must be set up on the specified template
# 3. The asset scaling variable needs to be set on the Projection Portfolio
# 4. The Portfolio Parameters Table that is used should include Initial Asset Scaling Type of '4' in the data table
# 5. The Company Properties Table should be set to
#       Capital Method 'None',
#       Distribute Earnings: False
#       Tax Rate: 0
sba_template_name = "MYGA SBA Solver Template"                    # The name of the projection template to be used within the solver
starting_asset_table_name = "Initial Asset Scaling"          # The name of the starting assets table
epl_table_name = "EPL Inputs"                                # The name of the EPL Input Table
use_epl = False                                       # If True, the solver will use the EPL table to generate the EPL cash flows. If False, it will fully calculate liabilities on each loop

solver_final_asset_tolerance = 10000        # tolerance for remaining assets for the BEL solve - Higher tolerances will converge faster
solver_max_iterations = 5                   # The maximum number of attempts to solve for BEL. If max iterations is exceeded, the last closes guess outside the tolerance will be used
next_guess_range = 0.20                     # Check a 20% weighted average range around the last guess
