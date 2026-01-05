run.sh:
```
#!/bin/tcsh -f

/user/signoff.dsa/launcher/utils/set_input_env.py
source env_setup.csh

set job_rundir = `pwd`
set job_config = `pwd`/../job_config.yaml
echo "Job config file is: $job_config"

#  Run PT-SignOff selected stage.
set STAGE = $CONDITIONAL_FLOW

if ( $STAGE == "1_Link_Top" ) then
  $UPDATE_CONFIG --start --msg "Linking Design..." --config $job_config
  cd 10_LINK_TOP
  ./:init $TOP_DESIGN
  cd $TOP_DESIGN

  set SI_MODE   = "no_si"
  set PT_RUNDIR   = "sta-min_max-no_si-${CORNER_PROC}_${CORNER_VOLT}v_${CORNER_TEMP}c_${CORNER_RC}"
  pushd $job_rundir
  $UPDATE_CONFIG --msg "Linking design..." --config $job_config
  popd
  ./:run_link_sol ${CORNER_PROC}_${CORNER_VOLT}v_${CORNER_TEMP}c_${CORNER_RC}
    if ($status == 0) then
    $UPDATE_CONFIG --done --msg "Link design done. Please see 10_LINK_TOP/$TOP_DESIGN/$PT_RUNDIR/logs/link_design.log" --config $job_config
  else
    $UPDATE_CONFIG --fail --msg "Link design failed. Please see 10_LINK_TOP/$TOP_DESIGN/$PT_RUNDIR/logs/link_design.log" --config $job_config
  endif
endif

if ( $STAGE == "2_Refine_Star" ) then
  $UPDATE_CONFIG --start --msg "Star Post-processing..." --config $job_config
  source ./REFERENCE/PT_SIGNOFF/file_to_list.csh $BLOCKS_TO_POST_PROCESS BLOCKS_TO_POST_PROCESS

  set STAR_ENV_TCL  = `realpath ./REFERENCE/PT_SIGNOFF/make_star_env.tcl`

  foreach BLOCK ($BLOCKS_TO_POST_PROCESS)
    $STAR_ENV_TCL $BLOCK
  end

  # Refine
  cd 20_REFINE_STAR
  foreach BLOCK ($BLOCKS_TO_POST_PROCESS)
    ./:init_and_run_refine_SOL $BLOCK
  end
  cd ../

  $UPDATE_CONFIG --done --msg "Star Post-processing done." --config $job_config
endif

if ( $STAGE =~ "3_PT_*" ) then
  set SIGNOFF = `echo $STAGE | cut -d'_' -f2-`
  $UPDATE_CONFIG --start --msg "Running $SIGNOFF" --config $job_config
  cd 30_PT_RUN
  ./:init $TOP_DESIGN $SIGNOFF
  cd $SIGNOFF
  ./:run_ptso_sol ${CORNER_PROC}_${CORNER_VOLT}v_${CORNER_TEMP}c_${CORNER_RC} $SIGNOFF

  cd $job_rundir

  if ( $SIGNOFF == "PT_DSC" || $SIGNOFF == "PT_CDA" ) then
    if ( $SIGNOFF == "PT_DSC" ) then
      set SI_MODE    = "no_si"
      set PT_RUNDIR  = "sta-min_max-${SI_MODE}-${CORNER_PROC}_${CORNER_VOLT}v_${CORNER_TEMP}c_${CORNER_RC}" ; # common
    else if ( $SIGNOFF == "PT_CDA" ) then
      set SI_MODE   = "si"
      set PT_RUNDIR   = "sta-min_max-${SI_MODE}-${CORNER_PROC}_${CORNER_VOLT}v_${CORNER_TEMP}c_${CORNER_RC}" ; # common
    endif
  endif

endif


```

input_config.yaml
```
PT_SIGNOFF:
  color: "#f7ccff" 
  label: "HBM4/4E PT-SignOff (PT-DSC, PT-CANA, PT-CDA)"
  manual_link: "https://confluence.PrimeTime+Sign-Off"
  mlm_link: "https://mlm./PRIMETIME/summary"
  developer: ['th0715.kim']
  inputs:
    - name: DK_LIBRARY_SETUP
      type: file_input
      required: true
      default: /INPUT_EX/library_setup.HBM4E.tcl
      description: "DK library setup"

    - name: VERILOG_NETLIST_SETUP
      type: file_input
      required: true
      default: /INPUT_EX/verilog_netlist_setup.tcl
      description: "Verilog netlist & Blkstar setup"

    - name: PROCESS_PT
      type: text_input
      required: true
      description: "Process corner to run"

    - name: VOLTAGE_PT
      type: text_input
      required: true
      description: "Voltage to run"

    - name: TEMPERATURE_PT
      type: text_input
      required: true
      description: "Temperature to run"

    - name: BEOL_PT
      type: text_input
      required: true
      description: "BEOL corner to run"

    - name: TOP_DESIGN
      type: text_input
      required: true
      description: "Top module name to link"

    - name: BLOCKSTAR_POST_PROCESS_PATH
      type: textarea_input
      required: true
      default: " "

  conditional_input_flow:
    - flows: ["1_Link_Top", "2_Refine_Star", "3_PT_DSC", "3_PT_CANA", "3_PT_CDA"]

    - flow_names: ["2_Refine_Star", "3_PT_DSC", "3_PT_CANA", "3_PT_CDA"]
      name: BLOCKSTAR_ORIGINAL_INFO
      type: file_input
      required: true
      default: "/INPUT_EX/blockstar_original_info.tcl"

    - flow_names: ["2_Refine_Star"]
      name: BLOCKS_TO_POST_PROCESS
      type: file_input
      required: true
      default: "/INPUT_EX/blocks_to_post_process.tcl"

    - flow_names: ["2_Refine_Star"]
      name: STDCELL_CDL_FILE
      type: file_input
      required: true
      default: "/user/hbm32gmp00/VERIFY/CIR/STD_CIR/STD_CDL_LIST"

    - flow_names: ["3_PT_DSC", "3_PT_CANA", "3_PT_CDA"]
      name: BLOCKS_TO_BACK_ANNOTATE
      type: file_input
      required: true
      default: "/INPUT_EX/blocks_to_back_annotate.tcl"

    - flow_names: ["3_PT_DSC", "3_PT_CANA", "3_PT_CDA"]
      name: RTL_SPEF_TO_BACK_ANNOTATE
      type: file_input
      required: false
      default: /INPUT_EX/rtl_spef_setup.tcl


```