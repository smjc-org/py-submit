from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def shared_test_directory(tmp_path_factory: pytest.TempPathFactory) -> Path:
    dir = tmp_path_factory.mktemp("code")
    dir_adam = dir / "adam"
    dir_tfl = dir / "tfl"
    dir_macro = dir / "macro"
    dir_other = dir / "other"

    # adam sas files
    dir_adam.mkdir()
    (dir_adam / "adsl.sas").write_text("""
                                       proc datasets library = work memtype = data kill noprint;
                                       quit;

                                       /*SUBMIT BEGIN*/
                                       proc sql;
                                           create table adal as select * from rawdata.fp;
                                       quit;
                                       /*SUBMIT END*/

                                       proc report;
                                       quit;
                                       """)
    (dir_adam / "adae.sas").write_text("""
                                       proc datasets library = work memtype = data kill noprint;
                                       quit;

                                       /*====SUBMIT BEGIN====*/
                                       proc sql;
                                           create table adae as select * from rawdata.ae;
                                       quit;
                                       /*====SUBMIT END====*/

                                       proc report;
                                       quit;
                                       """)

    # tfl sas files
    dir_tfl.mkdir()
    (dir_tfl / "t1.sas").write_text("""
                                    proc datasets library = work memtype = data kill noprint;
                                    quit;

                                    /*=- *SUBMIT BEGIN=- **/
                                    proc sql;
                                        create table t1 as select * from adam.adsl;
                                    quit;
                                    /*=- *SUBMIT END=- **/

                                    proc report;
                                    quit;
                                    """)
    (dir_tfl / "t2.sas").write_text("""
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
                                    """)
    (dir_tfl / "t3.sas").write_text("""
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
                                    """)

    # macro sas files
    dir_macro.mkdir()
    (dir_macro / "macro1.sas").write_text("""
                                          %macro macro1;
                                              proc sql;
                                                  select * from adsl;
                                              quit;
                                          %mend macro1;
                                          """)
    (dir_macro / "macro2.sas").write_text("""
                                          %macro macro2;
                                              proc sql;
                                                  select * from adae;
                                              quit;

                                              /*====NOT SUBMIT BEGIN====*/
                                              proc report;
                                              quit;
                                              /*NOT SUBMIT END*/
                                          %mend macro2;
                                          """)

    # other directories which supposed to be excluded
    dir_other.mkdir()
    (dir_other / "q1.sas").write_text("""
                                      proc datasets library = work memtype = data kill noprint;
                                      quit;
                                      """)
    (dir_other / "q2.sas").write_text("""
                                      proc datasets library = work memtype = data kill noprint;
                                      quit;
                                      """)

    # other sas files which supposed to be excluded
    (dir / "fcmp.sas").write_text("""
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
                                   """)

    # other files whose suffix is not sas
    (dir / "other.txt").write_text("""I'm not a SAS file.""")
    return dir


@pytest.fixture(scope="session")
def shared_validate_directory(tmp_path_factory: pytest.TempPathFactory) -> Path:
    dir = tmp_path_factory.mktemp("validate")
    dir_adam = dir / "adam"
    dir_tfl = dir / "tfl"
    dir_macro = dir / "macro"

    # adam txt files
    dir_adam.mkdir()
    (dir_adam / "adsl.txt").write_text("""
                                       proc sql;
                                           create table adal as select * from rawdata.fp;
                                       quit;
                                       """)
    (dir_adam / "adae.txt").write_text("""
                                       proc sql;
                                           create table adae as select * from rawdata.ae;
                                       quit;
                                       """)

    # tfl txt files
    dir_tfl.mkdir()
    (dir_tfl / "t1.txt").write_text("""
                                    proc sql;
                                        create table t1 as select * from adam.adsl;
                                    quit;
                                    """)
    (dir_tfl / "t2.txt").write_text("""
                                    proc sql;
                                        create table t2 as select * from adam.adeff;
                                    quit;
                                    """)
    (dir_tfl / "t3.txt").write_text("""
                                    %macro inner_macro;
                                        proc sql;
                                            select * from adsl;
                                        quit;
                                    %mend inner_macro;
                                    %inner_macro;
                                    proc sql noprint;
                                        select * from adae;
                                    quit;
                                    """)

    # macro txt files
    dir_macro.mkdir()
    (dir_macro / "macro1.txt").write_text("""
                                          %macro macro1;
                                              proc sql;
                                                  select * from adsl;
                                              quit;
                                          %mend macro1;
                                          """)
    (dir_macro / "macro2.txt").write_text("""
                                          %macro macro2;
                                              proc sql;
                                                  select * from adae;
                                              quit;
                                          %mend macro2;
                                          """)
    return dir
