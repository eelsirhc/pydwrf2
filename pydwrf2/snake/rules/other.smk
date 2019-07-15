# An example collection of Snakemake rules imported in the main Snakefile.
import os

filepaths=dict()
if not os.path.exists("output/index"):
    from pydwrf2.wrf import common as wc
    wc._index(None,"output/index")
import json
filepaths = json.load(open("output/index","r"))

def generate_output_name(input_name,output_dir):
    x= os.path.join(os.path.dirname(input_name), 
                        output_dir,
		        os.path.basename(input_name))
    print(x)
    import sys
    sys.exit(1)
    return x

rule combined_wrfout:
    input:
        index="output/index",
        files=expand("output/intermediate/{filename}.{{diag}}",filename=filepaths.get("wrfout",[]))
    output:
        "output/final/wrfout.{diag}.nc"
    shell:
        """
        ncrcat {input.files} -o output/final/wrfout.{wildcards.diag}.nc
        """

rule diag_simple:
    input:
        "{filename}"
    output:
         "output/intermediate/{filename}.{diag}"
    shell:
        "pydwrf2 {wildcards.diag} {input} {output}"


# make the index file in the parent directory
rule make_index:
    output:
        "output/index"
    run:
        from pydwrf2.wrf import common as wc
        wc._index(None,output[0])
        import json
        filepaths = json.load(open(output[0],'r'))

# copy namelist
rule copy_namelist:
     input:
        "namelist.input"
     output:
          "output/namelist.input"
     shell:
        "cp {input} {output}"