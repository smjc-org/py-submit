# 定义测试用例的验证文件内容

content_validate_adsl = """
proc sql;
    create table adal as select * from rawdata.fp;
quit;
"""

content_validate_addv = """
proc sql;
    create table adae as select * from rawdata.ae;
quit;
"""

content_validate_t1 = """
proc sql;
    create table t1 as select * from adam.adsl;
quit;
"""

content_validate_t2 = """
proc sql;
    create table t2 as select * from adam.adeff;
quit;
"""

content_validate_t3 = """
%macro inner_macro;
    proc sql;
        select * from adsl;
    quit;
%mend inner_macro;
%inner_macro;
proc sql noprint;
    select * from adae;
quit;
"""

content_validate_macro1 = """
%macro macro1;
    proc sql;
        select * from adsl;
    quit;
%mend macro1;
"""

content_validate_macro2 = """
%macro macro2;
    proc sql;
        select * from adae;
    quit;
%mend macro2;
"""
