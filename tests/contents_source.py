# 定义测试用例的源文件内容

content_source_adsl = """
proc datasets library = work memtype = data kill noprint;
quit;

/*SUBMIT BEGIN*/
proc sql;
    create table adal as select * from rawdata.fp;
quit;
/*SUBMIT END*/

proc report;
quit;
"""

content_source_addv = """
proc datasets library = work memtype = data kill noprint;
quit;

/*====SUBMIT BEGIN====*/
proc sql;
    create table adae as select * from rawdata.ae;
quit;
/*====SUBMIT END====*/

proc report;
quit;
"""

content_source_t1 = """
proc datasets library = work memtype = data kill noprint;
quit;

/*=- *SUBMIT BEGIN=- **/
proc sql;
    create table t1 as select * from adam.adsl;
quit;
/*=- *SUBMIT END=- **/

proc report;
quit;
"""

content_source_t2 = """
proc datasets library = work memtype = data kill noprint;
quit;

%let id = %str();

/*====SUBMIT BEGIN====*/
proc sql;
    create table t2 as select * from adam.adeff&id;
quit;
/*====SUBMIT END====*/

proc report;
quit;
"""

content_source_t3 = """
proc datasets library = work memtype = data kill noprint;
quit;

/*SUBMIT BEGIN*/
%macro inner_macro;
    proc sql;
        select * from adsl;
    quit;

    /*NOT SUBMIT BEGIN*/
    proc report;
    quit;
    /*NOT SUBMIT END*/
%mend inner_macro;
%inner_macro;
proc sql noprint;
    select * from adae;
quit;
/*SUBMIT END*/

proc report;
quit;
"""

content_source_macro1 = """
%macro macro1;
    proc sql;
        select * from adsl;
    quit;
%mend macro1;
"""

content_source_macro2 = """
%macro macro2;
    proc sql;
        select * from adae;
    quit;

    /*====NOT SUBMIT BEGIN====*/
    proc report;
    quit;
    /*NOT SUBMIT END*/
%mend macro2;
"""

content_source_q1 = """
proc datasets library = work memtype = data kill noprint;
quit;
"""

content_source_q2 = """
proc datasets library = work memtype = data kill noprint;
quit;
"""

content_source_fcmp = """
proc datasets library = work memtype = data kill noprint;
quit;
/*SUBMIT BEGIN*/
proc fcmp outlib = work.funcs.funcs;
    function add(x, y);
        return (x + y);
    endsub;
quit;
/*SUBMIT END*/
proc report;
quit;
"""

content_source_other = """
I'm not a SAS file.
"""
