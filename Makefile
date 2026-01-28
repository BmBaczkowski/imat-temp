# GNU Makefile 
# 
# generate BIDS raw dataset from source dataset

#------------------------------------------------------------------------------
# LOCAL VARS
#------------------------------------------------------------------------------

SOURCE-CODE				:= code-source2raw/imat-spc2
code-dir				:= $(SOURCE-CODE)/imat-spc2-code-bids

RAW						:= raw-datasets
data-bids-dir			:= $(RAW)/imat-spc2-data-raw

PTB-CODE				:= code-ptb
ptb-code-dir			:= $(PTB-CODE)/imat-spc2-ptb

SOURCE					:= source-datasets/imat-spc2
data-biopac-dir 		:= $(SOURCE)/imat-spc2-data-biopac
data-smi-dir 			:= $(SOURCE)/imat-spc2-data-smi-samples
data-limesurvey-dir 	:= $(SOURCE)/imat-spc2-data-limesurvey
data-ptb-dir 			:= $(SOURCE)/imat-spc2-data-ptb
subjectkeyfile			:= $(SOURCE)/subjectkey.json

ptb-code-hash			:= 3130403c773fd734b909085c90ee8cd8
biopac-hash				:= c1ca3ef0602137a276b5450cb7ed1995 
limesurvey-hash			:= 8085ad0ddc18ad198567c0eca3802ec7 
ptb-hash				:= b1785b8f1d1a7236feb63b6020b86904 
smi-hash				:= 8b1ecc03509e8adc825a8093351df4e3 
subjectkeyfile-hash		:= 0313c8f6b33da7ad01c951f5fcf38ac1

nsubjects				:= 37
acronym					:= imat-spc2


#------------------------------------------------------------------------------
# DOCKER UTILS
#------------------------------------------------------------------------------
.PHONY: test-docker build-docker

build-docker: \
	$(code-dir)/dockerfiles/Dockerfile \
	$(code-dir)/dockerfiles/requirements.txt
	docker build -t python:bids-env -f $< $(<D)

# command to save docker image
# docker save python:bids-env | gzip > $(code-dir)/dockerfiles/dockerimage.tar.gz

# test docker container
test-docker:
	docker run --rm -it -v `pwd`:/home/dockeruser python:bids-env bash

# short-cut to run the docker code
run 	:= docker run --rm -i -v `pwd`:/home/dockeruser python:bids-env

#------------------------------------------------------------------------------
# UTILS
#------------------------------------------------------------------------------
.PHONY: checksumdir checksumfile

# get md5 checksum of directory(-ies)
# to run this command, use
# make checksumdir CHECKDIR="dir1 dir2"
checksumdir: \
	$(code-dir)/codefiles/utils/checksumdir.py 
	$(run) ./$< $(CHECKDIR)

checksumfile: \
	$(code-dir)/codefiles/utils/checksumfile.py 
	$(run) ./$< $(CHECKFILE)

#------------------------------------------------------------------------------
# ALL
#------------------------------------------------------------------------------
.PHONY: all

all: \
	$(data-bids-dir)/logfiles/bids_init.log \
	$(data-bids-dir)/logfiles/dataset_description.log \
	$(data-bids-dir)/logfiles/participants.log \
	$(data-bids-dir)/logfiles/ptb.log \
	$(data-bids-dir)/logfiles/stai_trait.log \
	$(data-bids-dir)/logfiles/ius.log \
	$(data-bids-dir)/logfiles/free_text_data.log \
	$(data-bids-dir)/logfiles/free_text_questions.log \
	$(data-bids-dir)/logfiles/ratings_tasks_with_pairs.log \
	$(data-bids-dir)/logfiles/ratings_tasks_with_shocks.log \
	$(data-bids-dir)/logfiles/logbook.log \
	$(data-bids-dir)/logfiles/beh_task-01.log \
	$(data-bids-dir)/logfiles/beh_task-02.log \
	$(data-bids-dir)/logfiles/beh_task-03.log \
	$(data-bids-dir)/logfiles/beh_task-04.log \
	$(data-bids-dir)/logfiles/biopac.log \
	$(data-bids-dir)/logfiles/smi.log \
	$(data-bids-dir)/logfiles/recodeids.log \
	$(data-bids-dir)/logfiles/compress.log \
	$(data-bids-dir)/logfiles/sourcecode.log 

#------------------------------------------------------------------------------
# CLEAN
#------------------------------------------------------------------------------
.PHONY: \
	cleanall \
	clean-init \
	clean-agnostic \
	clean-sourcecode \
	clean-ptb \
	clean-phenotype \
	clean-assessment \
	clean-beh

clean-init: 
	rm -f $(data-bids-dir)/logfiles/bids_init.log
	rm -f $(data-bids-dir)/.bidsignore
	rm -f $(data-bids-dir)/README.md
	rm -f $(data-bids-dir)/CHANGES
	rm -f $(data-bids-dir)/LICENSE

clean-agnostic: 
	rm -f $(data-bids-dir)/logfiles/dataset_description.log 
	rm -f $(data-bids-dir)/dataset_description.json
	rm -f $(data-bids-dir)/logfiles/participants.log 
	rm -f $(data-bids-dir)/participants.tsv
	rm -f $(data-bids-dir)/participants.json
 
clean-ptb: 
	rm -fr $(data-bids-dir)/code-psychtoolbox
	rm -f $(data-bids-dir)/logfiles/ptb.log

clean-sourcecode: 
	rm -fr $(data-bids-dir)/code-source2raw
	rm -f $(data-bids-dir)/logfiles/sourcecode.log

clean-phenotype: 
	rm -fr $(data-bids-dir)/phenotype
	rm -f $(data-bids-dir)/logfiles/stai_trait.log
	rm -f $(data-bids-dir)/logfiles/ius.log

clean-assessment:
	rm -fr $(data-bids-dir)/assessment
	rm -f $(data-bids-dir)/logfiles/free_text*
	rm -f $(data-bids-dir)/logfiles/ratings_*
	rm -f $(data-bids-dir)/logfiles/logbook.log

clean-beh:
	rm -fr $(data-bids-dir)/sub*
	rm -f $(data-bids-dir)/logfiles/beh_*.log
	rm -f $(data-bids-dir)/logfiles/biopac.log
	rm -f $(data-bids-dir)/logfiles/smi.log
	rm -f $(data-bids-dir)/task*.json

cleanall: \
	clean-init \
	clean-agnostic \
	clean-ptb \
	clean-sourcecode \
	clean-phenotype \
	clean-assessment \
	clean-beh
	rm -fr $(data-bids-dir)/logfiles

#------------------------------------------------------------------------------
# INIT DATA STRUCTURE 
#------------------------------------------------------------------------------

$(data-bids-dir)/logfiles:
	mkdir $@

$(data-bids-dir)/logfiles/bids_init.log: \
	$(code-dir)/codefiles/bids_init.py \
	| $(data-bids-dir) \
	$(data-bids-dir)/logfiles
	$(run) ./$< $(word 1,$|)

#------------------------------------------------------------------------------
# CHECK MD5 HASH OF THE SOURCE DATA
#------------------------------------------------------------------------------

# check if the md5 checksum of source data directories match
$(data-bids-dir)/logfiles/checksumdir.log: \
	$(code-dir)/codefiles/utils/checksumdir.py \
	$(data-biopac-dir) \
	$(data-limesurvey-dir) \
	$(data-ptb-dir) \
	$(data-smi-dir) \
	$(ptb-code-dir) \
	| $(data-bids-dir)/logfiles
	$(run) ./$^ \
	--hash $(biopac-hash) \
	$(limesurvey-hash) \
	$(ptb-hash) \
	$(smi-hash) \
	$(ptb-code-hash) \
	--log-output-dir $|

# check if the md5 checksum of keyfile to recode ids is correct 
$(data-bids-dir)/logfiles/checksumkeyfile.log: \
	$(code-dir)/codefiles/utils/checksumfile.py \
	$(subjectkeyfile) \
	| $(data-bids-dir)/logfiles
	$(run) ./$^ --hash $(subjectkeyfile-hash) --log-output-dir $|

#------------------------------------------------------------------------------
# MODALITY AGNOSTIC FILES
#------------------------------------------------------------------------------

# dataset_description.json
$(data-bids-dir)/logfiles/dataset_description.log: \
	$(code-dir)/codefiles/bids_dataset_description.py \
	$(data-bids-dir)/logfiles/checksumdir.log \
	| $(data-bids-dir)
	$(run) ./$< $|

# participants.tsv
$(data-bids-dir)/logfiles/participants.log: \
	$(code-dir)/codefiles/bids_participants.py \
	$(data-bids-dir)/logfiles/checksumdir.log \
	| $(data-limesurvey-dir) $(data-bids-dir)
	$(run) ./$< $|

#------------------------------------------------------------------------------
# PSYCHTOOLBOX CODE
#------------------------------------------------------------------------------

# code-psychtoolbox/
$(data-bids-dir)/code-psychtoolbox:
	mkdir $@

$(data-bids-dir)/logfiles/ptb.log: \
	$(code-dir)/codefiles/bids_ptb.py \
	$(data-bids-dir)/logfiles/checksumdir.log \
	| $(ptb-code-dir) \
	$(data-bids-dir)/code-psychtoolbox \
	$(data-bids-dir)/logfiles
	$(run) ./$< $|

#------------------------------------------------------------------------------
# CODE FROM SOURCE TO RAW DATA
#------------------------------------------------------------------------------

$(data-bids-dir)/logfiles/sourcecode.log: \
	$(code-dir)/codefiles/bids_sourcecode.py \
	| $(code-dir) \
	$(data-bids-dir) \
	$(data-bids-dir)/logfiles
	$(run) ./$< $| $(acronym) 

#------------------------------------------------------------------------------
# PHENOTYPIC AND ASSESSMENT DATA
#------------------------------------------------------------------------------

# phenotype/
$(data-bids-dir)/phenotype:
	mkdir $@

$(data-bids-dir)/logfiles/stai_trait.log: \
	$(code-dir)/codefiles/bids_phenotype_stai.py \
	$(data-bids-dir)/logfiles/checksumdir.log \
	| $(data-limesurvey-dir) \
	$(data-bids-dir)/phenotype \
	$(data-bids-dir)/logfiles
	$(run) ./$< $|

$(data-bids-dir)/logfiles/ius.log: \
	$(code-dir)/codefiles/bids_phenotype_ius.py \
	$(data-bids-dir)/logfiles/checksumdir.log \
	| $(data-limesurvey-dir) \
	$(data-bids-dir)/phenotype \
	$(data-bids-dir)/logfiles
	$(run) ./$< $|

# assessment/
$(data-bids-dir)/assessment:
	mkdir $@

$(data-bids-dir)/logfiles/free_text_data.log: \
	$(code-dir)/codefiles/bids_assessment_data.py \
	$(data-bids-dir)/logfiles/checksumdir.log \
	| $(data-limesurvey-dir) \
	$(data-bids-dir)/assessment \
	$(data-bids-dir)/logfiles
	$(run) ./$< $|

$(data-bids-dir)/logfiles/free_text_questions.log: \
	$(code-dir)/codefiles/bids_assessment_questions.py \
	$(data-bids-dir)/logfiles/checksumdir.log \
	| $(data-bids-dir)/assessment \
	$(data-bids-dir)/logfiles
	$(run) ./$< $|

$(data-bids-dir)/logfiles/ratings_tasks_with_pairs.log: \
	$(code-dir)/codefiles/bids_assessment_rating_pairs.py \
	$(data-bids-dir)/logfiles/checksumdir.log \
	| $(data-limesurvey-dir) \
	$(data-bids-dir)/assessment \
	$(data-bids-dir)/logfiles
	$(run) ./$< $|

$(data-bids-dir)/logfiles/ratings_tasks_with_shocks.log: \
	$(code-dir)/codefiles/bids_assessment_rating_shocks.py \
	$(data-bids-dir)/logfiles/checksumdir.log \
	| $(data-biopac-dir) \
	$(data-bids-dir)/assessment \
	$(data-bids-dir)/logfiles
	$(run) ./$< $|

$(data-bids-dir)/logfiles/logbook.log: \
	$(code-dir)/codefiles/bids_assessment_logbook.py \
	$(data-bids-dir)/logfiles/checksumdir.log \
	| $(data-biopac-dir) \
	$(data-bids-dir)/assessment \
	$(data-bids-dir)/logfiles
	$(run) ./$< $|

#------------------------------------------------------------------------------
# BEHAVIOURAL DATA
#------------------------------------------------------------------------------

# make 'beh' sub-directories for each subject
$(data-bids-dir)/logfiles/beh_dir_maker.log: \
	$(code-dir)/codefiles/utils/make_beh_subdirs.py \
	$(data-bids-dir)/logfiles/checksumdir.log \
	| $(data-ptb-dir) \
	$(data-bids-dir) \
	$(data-bids-dir)/logfiles
	$(run) ./$< $|

# task01
$(data-bids-dir)/logfiles/beh_task-01.log: \
	$(code-dir)/codefiles/bids_task01.py \
	$(code-dir)/codefiles/utils/utils.py \
	$(code-dir)/codefiles/utils/task01_events.py \
	$(code-dir)/codefiles/utils/task01_afc.py \
	$(data-bids-dir)/logfiles/beh_dir_maker.log \
	| $(data-ptb-dir) \
	$(data-bids-dir) \
	$(data-bids-dir)/logfiles
	$(run) ./$< $|

# task02
$(data-bids-dir)/logfiles/beh_task-02.log: \
	$(code-dir)/codefiles/bids_task02.py \
	$(code-dir)/codefiles/utils/utils.py \
	$(code-dir)/codefiles/utils/task02_events.py \
	$(code-dir)/codefiles/utils/task02_beh.py \
	$(data-bids-dir)/logfiles/beh_dir_maker.log \
	| $(data-ptb-dir) \
	$(data-bids-dir) \
	$(data-bids-dir)/logfiles
	$(run) ./$< $|

# task03
$(data-bids-dir)/logfiles/beh_task-03.log: \
	$(code-dir)/codefiles/bids_task03.py \
	$(code-dir)/codefiles/utils/utils.py \
	$(code-dir)/codefiles/utils/task03_events.py \
	$(code-dir)/codefiles/utils/task03_beh.py \
	$(data-bids-dir)/logfiles/beh_dir_maker.log \
	| $(data-ptb-dir) \
	$(data-bids-dir) \
	$(data-bids-dir)/logfiles
	$(run) ./$< $|

# task04
$(data-bids-dir)/logfiles/beh_task-04.log: \
	$(code-dir)/codefiles/bids_task04.py \
	$(code-dir)/codefiles/utils/utils.py \
	$(code-dir)/codefiles/utils/task04_events.py \
	$(code-dir)/codefiles/utils/task04_beh.py \
	$(data-bids-dir)/logfiles/beh_dir_maker.log \
	| $(data-ptb-dir) \
	$(data-bids-dir) \
	$(data-bids-dir)/logfiles
	$(run) ./$< $|

#------------------------------------------------------------------------------
# BIOPAC DATA
#------------------------------------------------------------------------------

$(data-bids-dir)/logfiles/biopac.log: \
	$(code-dir)/codefiles/bids_biopac.py \
	$(code-dir)/codefiles/utils/utils_biopac.py \
	$(data-bids-dir)/logfiles/beh_dir_maker.log \
	| $(data-biopac-dir) \
	$(data-bids-dir) \
	$(data-bids-dir)/logfiles
	$(run) ./$< $|

#------------------------------------------------------------------------------
# EYE-TRACKING DATA
#------------------------------------------------------------------------------

$(data-bids-dir)/logfiles/smi.log: \
	$(code-dir)/codefiles/bids_smi.py \
	$(code-dir)/codefiles/utils/utils_smi.py \
	$(data-bids-dir)/logfiles/beh_dir_maker.log \
	| $(data-smi-dir) \
	$(data-ptb-dir) \
	$(data-bids-dir) \
	$(data-bids-dir)/logfiles
	$(run) ./$< $|

#------------------------------------------------------------------------------
# RE-CODE IDS
#------------------------------------------------------------------------------

$(data-bids-dir)/logfiles/recodeids.log: \
	$(code-dir)/codefiles/recode_ids.py \
	$(subjectkeyfile) \
	$(code-dir)/codefiles/utils/utils_recode.py \
	$(data-bids-dir)/logfiles/beh_task-01.log \
	$(data-bids-dir)/logfiles/beh_task-02.log \
	$(data-bids-dir)/logfiles/beh_task-03.log \
	$(data-bids-dir)/logfiles/beh_task-04.log \
	$(data-bids-dir)/logfiles/biopac.log \
	$(data-bids-dir)/logfiles/smi.log \
	$(data-bids-dir)/logfiles/checksumkeyfile.log \
	| $(data-bids-dir) \
	$(data-bids-dir)/logfiles
	$(run) ./$< $(word 2,$^) $(nsubjects) $|


#------------------------------------------------------------------------------
# COMPRESS BIOPAC AND SMI TSV FILES TO GZIP
#------------------------------------------------------------------------------

$(data-bids-dir)/logfiles/compress.log: \
	$(code-dir)/codefiles/compress_files.py \
	| $(data-bids-dir) \
	$(data-bids-dir)/logfiles
	$(run) ./$< $|

