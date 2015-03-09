"""
Create SPM examples stored in nidm/nidm-results/spm by using the class 
templates available in nidm/nidm-results/terms/templates

@author: Camille Maumet <c.m.j.maumet@warwick.ac.uk>
@copyright: University of Warwick 2013-2014
"""
import os
from create_example_from_templates import ExampleFromTemplate

import sys

RELPATH = os.path.dirname(os.path.abspath(__file__))
NIDMRESULTSPATH = os.path.dirname(RELPATH)
# Append parent script directory to path
sys.path.append(os.path.join(NIDMRESULTSPATH, os.pardir, os.pardir, "scripts"))
from Constants import STATO_OLS_STR

def main():
	nidm_classes = {
		"DesignMatrix": dict(
			design_matrix_id='niiri:design_matrix_id', 
			label="Design Matrix", 
			location="file:///path/to/DesignMatrix.csv",
			format="text/csv", 
			filename="DesignMatrix.csv", 
			design_matrix_png_id="niiri:design_matrix_png_id"),
		"Image-DesignMatrix": dict(
			image_id="niiri:design_matrix_png_id",
			location="file:///path/to/DesignMatrix.png",
			filename="DesignMatrix.png",
			format="image/png"
			),
		"Data": dict(
			data_id='niiri:data_id',
			label="Data",
			scaling="true",
			target=100
			),
		"ErrorModel": dict(
			error_model_id="niiri:error_model_id",
			noise_distribution="nidm:GaussianDistribution",
			variance_homo="true",
			variance_spatial="nidm:SpatiallyLocalModel",
			dependence="nidm:IndependentError",
			dependence_spatial="nidm:SpatiallyLocalModel"
			),
		"CustomMaskMap": dict(
			custom_mask_id="niiri:mask_id_1",
			label="Custom mask",
			location="file:///path/to/CustomMask.nii.gz",
			filename="CustomMask.nii.gz",
			format="image/nifti",
			coordinate_space_id="niiri:coordinate_space_id_1",
			sha="e43b6e01b0463fe7d40782137867a..."
			),
		"ModelPEUsedCustomMaskMap": dict(
			model_pe_id="niiri:model_pe_id",
			custom_mask_map_id="niiri:mask_id_1"
			),
		"DerivedMap-CustomMaskMap": dict(
			derived_from_map_id="niiri:mask_id_1_der",
			derived_map_type="nidm:CustomMaskMap",
			filename="user_custom_mask.nii",
			format="image/nifti",
			sha="e43b6e01b0463fe7d40782137867a...",
			map_id="niiri:mask_id_1"
			),
		"ModelParametersEstimation": dict(
			model_pe_id="niiri:model_pe_id",
			label="Model parameters estimation",
			est_method=STATO_OLS_STR,
			design_matrix_id="niiri:design_matrix_id",
			data_matrix_id="niiri:data_id",
			error_model_id="niiri:error_model_id",
			software_id="niiri:software_id"
			),
		"ParameterEstimateMap-1": dict(
			beta_map_id="niiri:beta_map_id_1",
			label="Beta Map 1",
			location="file:///path/to/ParameterEstimate_0001.nii.gz",
			filename="ParameterEstimate_0001.nii.gz",
			format="image/nifti",
			coordinate_space_id="niiri:coordinate_space_id_1",
			sha="e43b6e01b0463fe7d40782137867a...",
			param_est_id="niiri:model_pe_id"),
		"DerivedMapWithHeader-PE1": dict(
			derived_from_map_id="niiri:beta_map_id_1_der",
			derived_map_type="nidm:ParameterEstimateMap",
			filename="beta_0001.img",
			format="image/nifti",
			derived_from_map_header_id="niiri:original_pe_map_header_id",
			sha="e43b6e01b0463fe7d40782137867a...",
			format_header="image/nifti",
			filename_header="beta_0001.hdr",
			sha_header="e43b6e01b0463fe7d40782137867a...",
			map_id="niiri:beta_map_id_1"
			),
		"ParameterEstimateMap-2": dict(
			beta_map_id="niiri:beta_map_id_2",
			label="Beta Map 2",
			location="file:///path/to/ParameterEstimate_0002.nii",
			filename="ParameterEstimate_0002.nii.gz",
			format="image/nifti",
			coordinate_space_id="niiri:coordinate_space_id_1",
			sha="e43b6e01b0463fe7d40782137867a...",
			param_est_id="niiri:model_pe_id"),
		"CoordinateSpace-1": dict(
			coordinate_space_id="niiri:coordinate_space_id_1",
			label="Coordinate space 1",
			voxel_to_world_mapping="[[-3, 0, 0, 78],[0, 3, 0, -112],[0, 0, 3, -50],[0, 0, 0, 1]]",
			voxel_units="['mm', 'mm', 'mm']",
			voxel_size="[3, 3, 3]",
			coord_system="nidm:MNICoordinateSystem",
			number_of_dim="3",
			dimensions="[53,63,46]"),
		"ResidualMeanSquaresMap": dict(
			residual_mean_squares_map_id="niiri:residual_mean_squares_map_id",
			label="Residual Mean Squares Map",
			location="file:///path/to/ResidualMeanSquares.nii.gz",
			filename="ResidualMeanSquares.nii.gz",
			format="image/nifti",
			coordinate_space_id="niiri:coordinate_space_id_1",
			sha="e43b6e01b0463fe7d40782137867a...",
			param_est_id="niiri:model_pe_id"),
		"MaskMap": dict(
			mask_id="niiri:mask_id_2",
			label="Mask",
			location="file:///path/to/Mask.nii.gz",
			filename="Mask.nii.gz",
			format="image/nifti",
			coordinate_space_id="niiri:coordinate_space_id_1",
			sha="e43b6e01b0463fe7d40782137867a...",
			param_est_id="niiri:model_pe_id"),
		"DerivedMapWithHeader-Mask2": dict(
			derived_from_map_id="niiri:mask_id_2_der",
			derived_map_type="nidm:MaskMap",
			filename="mask.img",
			format="image/nifti",
			derived_from_map_header_id="niiri:original_mask_map_header_id",
			sha="e43b6e01b0463fe7d40782137867a...",
			format_header="image/nifti",
			filename_header="mask.hdr",
			sha_header="e43b6e01b0463fe7d40782137867a...",
			map_id="niiri:mask_id_2"
			),
		"ContrastWeights": dict(
			contrast_id="niiri:contrast_id",
			label="Contrast: Listening > Rest",
			value="[1, 0, 0]",
			statistic_type="nidm:TStatistic",
			contrast_name="listening > rest"
			),
		"ContrastEstimation": dict(
			contrast_estimation_id="niiri:contrast_estimation_id",
			label="Contrast estimation",
			software_id="niiri:software_id",
			mask_id="niiri:mask_id_2",
			residual_mean_squares_map_id="niiri:residual_mean_squares_map_id",
			design_matrix_id="niiri:design_matrix_id",
			contrast_id="niiri:contrast_id",
			param_est_map="niiri:beta_map_id_1"
			),
		"ContrastEstUsedParamEst-Con1PE2": dict(
			contrast_estimation_id="niiri:contrast_estimation_id",
			param_est_map="niiri:beta_map_id_2"
			),
		"ContrastMap": dict(
			contrast_map_id="niiri:contrast_map_id",
			label="Contrast Map: listening > rest",
			location="file:///path/to/Contrast.nii.gz",
			format="image/nifti",
			filename="Contrast.nii.gz",
			contrast_name="listening > rest",
			coordinate_space_id="niiri:coordinate_space_id_1",
			sha="e43b6e01b0463fe7d40782137867a...",
			contrast_est_id="niiri:contrast_estimation_id"),
		"ContrastStandardErrorMap": dict(
			contrast_standard_error_map_id="niiri:contrast_standard_error_map_id",
			label="Contrast Standard Error Map",
			location="file:///path/to/ContrastStandardError.nii.gz",
			format="image/nifti",
			filename="ContrastStandardError.nii.gz",
			coordinate_space_id="niiri:coordinate_space_id_1",
			sha="e43b6e01b0463fe7d40782137867a...",
			contrast_est_id="niiri:contrast_estimation_id"),
		"StatisticMap": dict(
			statistic_map_id="niiri:statistic_map_id",
			label="Statistic Map: listening > rest",
			location="file:///path/to/TStatistic.nii.gz",
			format="image/nifti",
			filename="TStatistic.nii.gz",
			statistic_type="nidm:TStatistic",
			contrast_name="listening > rest",
			error_dof="72.9999999990787",
			effect_dof="1",
			sha="e43b6e01b0463fe7d40782137867a...",
			coordinate_space_id="niiri:coordinate_space_id_1",
			contrast_est_id="niiri:contrast_estimation_id"),
		"DerivedMapWithHeader-StatMap": dict(
			derived_from_map_id="niiri:statistic_map_id_der",
			derived_map_type="nidm:StatisticMap",
			filename="spmT_0001.img",
			format="image/nifti",
			derived_from_map_header_id="niiri:statistic_original_map_header_id",
			sha="e43b6e01b0463fe7d40782137867a...",
			format_header="image/nifti",
			filename_header="spmT_0001.hdr",
			sha_header="e43b6e01b0463fe7d40782137867a...",
			map_id="niiri:statistic_map_id"
			),
		"HeightThreshold": dict(
			height_threshold_id="niiri:height_threshold_id",
			label="Height Threshold: p<0.05 (FWE)",
			value="5.23529984739211",
			thresh_type="p-value FWE",
			p_unc="7.62276079258051e-07",
			p_fwe="0.05"
			),
		"ExtentThreshold": dict(
			extent_threshold_id="niiri:extent_threshold_id",
			label="Extent Threshold: k>=0",
			cluster_size_vox="0",
			cluster_size_resels="0",
			p_unc="1",
			p_fwe="1"
			),
		"DisplayMaskMap": dict(
			display_map_id="niiri:display_map_id",
			label="Display Mask Map",
			location="file:///path/to/DisplayMask.nii.gz",
			format="image/nifti",
			filename="DisplayMask.nii.gz",
			coordinate_space_id="niiri:coordinate_space_id_2",
			sha="e43b6e01b0463fe7d40782137867a..."
			),
		"PeakDefinitionCriteria": dict(
			peak_definition_criteria_id="niiri:peak_definition_criteria_id",
			label="Peak Definition Criteria",
			max_num_peaks="3",
			min_dist_peaks="8.0"
			),
		"ClusterDefinitionCriteria": dict(
			cluster_definition_criteria_id="niiri:cluster_definition_criteria_id",
			label="Cluster Connectivity Criterion: 18",
			connectivity="nidm:voxel18connected"
			),
		"InferenceMaskMap": dict(
			inference_mask_id="niiri:sub_volume_id",
			label="Inference Mask Map",
			location="file:///path/to/InferenceMask.nii.gz",
			filename="InferenceMask.nii.gz",
			format="image/nifti",
			coordinate_space_id="niiri:coordinate_space_id_2",
			sha="e43b6e01b0463fe7d40782137867a..."
			),
		"CoordinateSpace-2": dict(
			coordinate_space_id="niiri:coordinate_space_id_2",
			label="Coordinate space 2",
			voxel_to_world_mapping="[[-3, 0, 0, 78],[0, 3, 0, -112],[0, 0, 3, -50],[0, 0, 0, 1]]",
			voxel_units="['mm', 'mm', 'mm']",
			voxel_size="[3, 3, 3]",
			coord_system="nidm:MNICoordinateSystem",
			number_of_dim="3",
			dimensions="[53,63,46]"),
		"Inference": dict(
			inference_id="niiri:inference_id",
			label="Inference",
			alternative_hyp="nidm:OneTailedTest",
			stat_map_id="niiri:statistic_map_id", 
			height_thresh_id="niiri:height_threshold_id", 
			extent_thresh_id="niiri:extent_threshold_id", 
			display_mask_id="niiri:display_map_id", 
			peak_def_id="niiri:peak_definition_criteria_id", 
			cluster_def_id="niiri:cluster_definition_criteria_id",
			mask_id="niiri:mask_id_2",
			software_id="niiri:software_id"
			),
		"InferenceUsedCustomMask": dict(
			inference_id="niiri:inference_id",
			custom_mask_id="niiri:sub_volume_id"
			),
		"ExcursionSetMap": dict(
			id="niiri:excursion_set_map_id",
			label="Excursion Set Map",
			location="file:///path/to/ExcursionSetMap.nii.gz",
			format="image/nifti",
			filename="ExcursionSetMap.nii.gz",
			cluster_label_map_id="niiri:cluster_label_map_id",
			max_intensity_projection_id="niiri:maximum_intensity_projection_id",
			coordinate_space_id="niiri:coordinate_space_id_1",
			sha="e43b6e01b0463fe7d40782137867a...",
			num_of_clusters="8",
			p_value="8.95949980872501e-14",
			inference_id="niiri:inference_id"
			),
		"Cluster-1": dict(
			cluster_id="niiri:cluster_0001",
			label="Cluster 0001",
			cluster_size_in_voxels="530",
			cluster_label_id="1",
			cluster_size_in_resels="23.1209189500945",
			p_value_unc="9.56276736481136e-52",
			p_value_fwe="0",
			p_value_fdr="7.65021389184909e-51",
			excursion_set_id="niiri:excursion_set_map_id"
			),
		"Cluster-2": dict(
			cluster_id="niiri:cluster_0002",
			label="Cluster 0002",
			cluster_size_in_voxels="445",
			cluster_label_id="2",
			cluster_size_in_resels="19.4128470430038",
			p_value_unc="3.91543427861809e-46",
			p_value_fwe="0",
			p_value_fdr="1.56617371144723e-45",
			excursion_set_id="niiri:excursion_set_map_id"
			),
		"Cluster-3": dict(
			cluster_id="niiri:cluster_0003",
			label="Cluster 0003",
			cluster_size_in_voxels="38",
			cluster_label_id="3",
			cluster_size_in_resels="1.6577262643464",
			p_value_unc="1.56592642027122e-09",
			p_value_fwe="1.39237954499549e-10",
			p_value_fdr="4.17580378738993e-09",
			excursion_set_id="niiri:excursion_set_map_id"
			),
		"Peak-1": dict(
			peak_id="niiri:peak_0001",
			label="Peak 0001",
			location="niiri:coordinate_0001",
			value="13.9346199035645",
			equiv_z="INF",
			p_value_unc="4.44089209850063e-16",
			p_value_fwe="0",
			p_value_fdr="6.3705194444993e-11",
			cluster_id="niiri:cluster_0001"
			),
		"Coordinate-1": dict(
			coordinate_id="niiri:coordinate_0001",
			label="Coordinate: 0001",
			coord_1="-60",
			coord_2="-28",
			coord_3="13"
			),
		"Peak-2": dict(
			peak_id="niiri:peak_0002",
			label="Peak 0002",
			location="niiri:coordinate_0002",
			value="11.3457498550415",
			equiv_z="INF",
			p_value_unc="4.44089209850063e-16",
			p_value_fwe="0",
			p_value_fdr="3.12855975726156e-10",
			cluster_id="niiri:cluster_0001"
			),
		"Coordinate-2": dict(
			coordinate_id="niiri:coordinate_0002",
			label="Coordinate: 0002",
			coord_1="-66",
			coord_2="-13",
			coord_3="4"
			),
		"Peak-3": dict(
			peak_id="niiri:peak_0003",
			label="Peak 0003",
			location="niiri:coordinate_0003",
			value="9.82185649871826",
			equiv_z="7.80404869241187",
			p_value_unc="2.99760216648792e-15",
			p_value_fwe="1.82057147135595e-10",
			p_value_fdr="9.95383070867767e-08",
			cluster_id="niiri:cluster_0001"
			),
		"Coordinate-3": dict(
			coordinate_id="niiri:coordinate_0003",
			label="Coordinate: 0003",
			coord_1="-63",
			coord_2="-7",
			coord_3="-2"
			),
		"Peak-4": dict(
			peak_id="niiri:peak_0004",
			label="Peak 0004",
			location="niiri:coordinate_0004",
			value="13.7208814620972",
			equiv_z="INF",
			p_value_unc="4.44089209850063e-16",
			p_value_fwe="0",
			p_value_fdr="6.3705194444993e-11",
			cluster_id="niiri:cluster_0002"
			),
		"Coordinate-4": dict(
			coordinate_id="niiri:coordinate_0004",
			label="Coordinate: 0004",
			coord_1="57",
			coord_2="-22",
			coord_3="13"
			),
		"Peak-5": dict(
			peak_id="niiri:peak_0005",
			label="Peak 0005",
			location="niiri:coordinate_0005",
			value="12.322901725769",
			equiv_z="INF",
			p_value_unc="4.44089209850063e-16",
			p_value_fwe="0",
			p_value_fdr="6.3705194444993e-11",
			cluster_id="niiri:cluster_0002"
			),
		"Coordinate-5": dict(
			coordinate_id="niiri:coordinate_0005",
			label="Coordinate: 0005",
			coord_1="66",
			coord_2="-13",
			coord_3="-2"
			),
		"Peak-6": dict(
			peak_id="niiri:peak_0006",
			label="Peak 0006",
			location="niiri:coordinate_0006",
			value="9.62070846557617",
			equiv_z="7.7026943536333",
			p_value_unc="6.66133814775094e-15",
			p_value_fwe="4.2237258135458e-10",
			p_value_fdr="1.58195372181651e-07",
			cluster_id="niiri:cluster_0002"
			),
		"Coordinate-6": dict(
			coordinate_id="niiri:coordinate_0006",
			label="Coordinate: 0006",
			coord_1="57",
			coord_2="-40",
			coord_3="7"
			),
		"Peak-7": dict(
			peak_id="niiri:peak_0007",
			label="Peak 0007",
			location="niiri:coordinate_0007",
			value="7.49709033966064",
			equiv_z="6.43494304364426",
			p_value_unc="6.17598194807556e-11",
			p_value_fwe="4.05099727462943e-06",
			p_value_fdr="0.000463130517859672",
			cluster_id="niiri:cluster_0003"
			),
		"Coordinate-7": dict(
			coordinate_id="niiri:coordinate_0007",
			label="Coordinate: 0007",
			coord_1="36",
			coord_2="-31",
			coord_3="-14"
			),
		"SearchSpaceMap": dict(
			search_space_id="niiri:search_space_id",
			location="file:///path/to/SearchSpace.nii.gz",
			filename="SearchSpace.nii.gz",
			label="Search Space Map",
			format="image/nifti",
			coordinate_space_id="niiri:coordinate_space_id_2",
			expected_num_voxels="0.553331387916112",
			expected_num_clusters="0.0889172687960151",
			height_critical_fwe05="5.23529984739211",
			height_critical_fdr05="6.22537899017334",
			smallest_size_fwe05="1",
			smallest_size_fdr05="3",
			search_vol_voxels="65593",
			search_vol_units="1771011",
			resel_size="22.9229643140043",
			search_vol_resels="2552.68032521656",
			search_vol_resels_geom="[3, 72.3216126440484, 850.716735116472, 2552.68032521656]",
			noise_fwhm_in_voxels="[2.95881189165801, 2.96628446669584, 2.61180425626264]",
			noise_fwhm_in_units="[8.87643567497404, 8.89885340008753, 7.83541276878791]",
			random_field_station="false",
			sha="e43b6e01b0463fe7d40782137867a...",
			inference_id="niiri:inference_id"
			),
		"DerivedMapWithHeader": dict(
			derived_from_map_id="niiri:contrast_map_id_der",
			derived_map_type="nidm:ContrastMap",
			filename="con_0001.img",
			format="image/nifti",
			derived_from_map_header_id="niiri:original_contrast_map_header_id",
			sha="e43b6e01b0463fe7d40782137867a...",
			format_header="image/nifti",
			filename_header="con_0001.hdr",
			sha_header="e43b6e01b0463fe7d40782137867a...",
			map_id="niiri:contrast_map_id"
			),
		"DerivedMapWithHeader-2": dict(
			derived_from_map_id="niiri:beta_map_id_2_der",
			derived_map_type="nidm:ParameterEstimateMap",
			filename="beta_0002.img",
			format="image/nifti",
			derived_from_map_header_id="niiri:original_pe_map_header_2_id",
			sha="e43b6e01b0463fe7d40782137867a...",
			format_header="image/nifti",
			filename_header="beta_0002.hdr",
			sha_header="e43b6e01b0463fe7d40782137867a...",
			map_id="niiri:beta_map_id_2"
			),
		"DerivedMapWithHeader-3": dict(
			derived_from_map_id="niiri:statistic_map_id_der",
			derived_map_type="nidm:StatisticMap",
			filename="spmT_0001.img",
			format="image/nifti",
			derived_from_map_header_id="niiri:statistic_original_map_header_id",
			sha="e43b6e01b0463fe7d40782137867a...",
			format_header="image/nifti",
			filename_header="spmT_0001.hdr",
			sha_header="e43b6e01b0463fe7d40782137867a...",
			map_id="niiri:statistic_map_id"
			),
		"NIDMBundle": dict(
			bundle_id="niiri:spm_results_id",
			label="SPM Results",
			object_model="nidm:SPMResults",
			version="0.2.0",
			time="2014-05-19T10:30:00.000+01:00"
			),
		"SPM_ReselsPerVoxelMap": dict(
			resels_per_voxel_map_id="niiri:resels_per_voxel_map_id",
			label="Resels per Voxel Map",
			location="file:///path/to/ReselsPerVoxel.nii.gz",
			filename="ReselsPerVoxel.nii.gz",
			format="image/nifti",
			coordinate_space_id="niiri:coordinate_space_id_1",
			sha="e43b6e01b0463fe7d40782137867a...",
			model_pe_id="niiri:model_pe_id"
			),
		"SPM_InferenceUsedRPVMap": dict(
			inference_id="niiri:inference_id",
			resels_per_voxel_map_id="niiri:resels_per_voxel_map_id"
		),
		"DerivedMapWithHeader-4": dict(
			derived_from_map_id="niiri:resels_per_voxel_map_id_der",
			derived_map_type="spm:ReselsPerVoxelMap",
			filename="RPV.img",
			format="image/nifti",
			derived_from_map_header_id="niiri:original_rpv_map_header_id",
			sha="e43b6e01b0463fe7d40782137867a...",
			format_header="image/nifti",
			filename_header="RPV.hdr",
			sha_header="e43b6e01b0463fe7d40782137867a...",
			map_id="niiri:resels_per_voxel_map_id"
			),
		"ClusterLabelsMap": dict(
			cluster_label_map_id="niiri:cluster_label_map_id",
			location="file:///path/to/ClusterLabels.nii.gz",
			filename="ClusterLabels.nii.gz",
			format="image/nifti"
			),
		"SPM_Software": dict(
			software_id="niiri:software_id",
			software_type="nidm:SPM",
			label="SPM",
			version="SPM12b",
			revision="5853"
			),
		"Image": dict(
			image_id="niiri:maximum_intensity_projection_id",
			location="file:///path/to/MaximumIntensityProjection.png",
			filename="MaximumIntensityProjection.png",
			format="image/png"
			),
		"GrandMeanMap": dict(
			grand_mean_map_id="niiri:grand_mean_map_id",
			label="Grand Mean Map",
			location="file:///path/to/GrandMean.nii.gz",
			filename="GrandMean.nii.gz",
			format="image/nifti",
			masked_median="115",
			coordinate_space_id="niiri:coordinate_space_id_1",
			sha="e43b6e01b0463fe7d40782137867a...",
			model_pe_id="niiri:model_pe_id"
			)
		}

	NIDM_SPM_DIR = os.path.join(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))), 'spm')
	ttl_file = os.path.join(NIDM_SPM_DIR, 'spm_results.ttl')
	example = ExampleFromTemplate(nidm_classes, ttl_file, False)
	example.create_example()

if __name__ == '__main__':
	main()
