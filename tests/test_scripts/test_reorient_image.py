import ndmg
from ndmg import preproc as mgp
from ndmg.utils import gen_utils as mgu
from ndmg.register import gen_reg as mgr
from ndmg.track import gen_track as mgt
from ndmg.graph import gen_graph as mgg
from ndmg.utils.bids_utils import name_resource
from unittest.mock import Mock, MagicMock	
import nibabel as nib
import numpy as np 
import pytest
import os

#create mock namer
namer = MagicMock()

def test_reorient_image(tmp_path): 
	d = tmp_path/"sub"
	d.mkdir()
	#set namer to point to temp directory 
	namer.dirs = {'output': {'prep_anat': d } }

	# define correct input data path
	# /mnt/labbook/output/untracked/dwi/preproc/eddy_corrected_data.nii.gz
	# eddy corrected dwi file
	img_in = '../test_data/inputs/reorient_image/sub-0025864_ses-1_T1w.nii.gz' 

	# define correct output data path 
	t1w_out_control_path = '../test_data/outputs/reorient_image/sub-0025864_ses-1_T1w_reor_RAS.nii.gz' 

	#load correct outputs
	t1w_out_control = nib.load(t1w_out_control_path).get_fdata()

	#call function and save in temp folder
	t1w = mgu.reorient_img(img_in, namer)

	#load outputs
	t1w_out = nib.load(t1w).get_fdata()

	#test dwi_prep and bvec
	assert np.allclose (t1w_out, t1w_out_control)


#requires most up to date pytest for tmp_path to work
