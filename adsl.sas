%let syscc = 0;

dm log 'clear';
dm output 'clear';
dm odsresult 'clear';

proc datasets lib=work kill memtype=data nolist;
quit;

/* SUBMIT BEGIN */
proc sql noprint;
    create table adsl as
        select ...
quit;

/* NOT SUBMIT BEGIN */
proc means data = adsl;
    var age;
run;
/* NOT SUBMIT END */

proc sort data = adsl;
    by usubjid;
run;
/* SUBMIT END */

%sm_log;
%error;