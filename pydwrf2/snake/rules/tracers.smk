tracer_list = ["water","icemass"]

rule tracer_all:
    input:
        files = expand("output/final/wrfout.{var}.nc", var=tracer_list)
    output:
        "file"
    shell:
        """ 
        touch "file"
        """
        