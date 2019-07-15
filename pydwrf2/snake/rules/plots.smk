#plot rules


rule diag_plot:
     input:
        "output/final/wrfout.{diag}.nc"
     output:
        "output/pdf/{diag}.pdf"
     shell:
        "pydwrf2 plot-{wildcards.diag} {input} {output}"

rule quick_plot:
     input:
        "output/final/wrfout.{diag}.nc"
     output:
        "output/pdf/plot_{diag}.pdf"
     shell:
        "pydwrf2 plot {wildcards.diag} {input} {output}"

ruleorder: quick_plot > diag_plot