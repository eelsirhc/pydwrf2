import numpy as np

delta_ls = 30
low_ls = 0
high_ls = 360
ls_range = np.arange(low_ls, high_ls+delta_ls, delta_ls)
formatted_ls = [format(x,"05.1f") for x in ls_range]

rule database_index:
     input:
        files="output/final/wrfout.ls.nc"
     output:
        "output/database/database_index.csv"
     shell:
        """
        pydwrf2 database index
        """     
rule database_index_single_ls:
     input:
        "output/database/database_index.csv"
     output:
        "output/database/database-ls-{low}-{high}.csv"
     shell:
          """pydwrf2 database index_ls {wildcards.low} {wildcards.high}"""

rule aggregate:
     input:
        "output/database/database-ls-{low}-{high}.csv"
     output:
        "output/database/database-ls-{low}-{high}-{variables}.nc"
     shell:
          """pydwrf2 database aggregate {wildcards.variables} {input} {output}"""

rule combined_database:
     input:
        expand("output/database/database-ls-{low}-{high}-{{variables}}.nc",zip,low=formatted_ls[:-1], high=formatted_ls[1:])
     output:
        "output/final/database_{variables}.nc"
     shell:
          """
          ncecat -O -u time {input} -o {output}
          """


