'''Python implementation of NI-DM (for statistical results)

@author: Camille Maumet <c.m.j.maumet@warwick.ac.uk>
@copyright: University of Warwick 2013-2014
'''

from prov.model import ProvBundle, Namespace, ProvRecord, ProvExceptionCannotUnifyAttribute, graph, ProvEntity, Identifier
import prov.model.graph
from prov.model import PROV
import os
import numpy as np
import nibabel as nib


NIDM = Namespace('nidm', "http://www.incf.org/ns/nidash/nidm#")
NIIRI = Namespace("niiri", "http://iri.nidash.org/")
CRYPTO = Namespace("crypto", "http://www.w3.org/2000/10/swap/crypto#")
FSL = Namespace("fsl", "http://www.incf.org/ns/nidash/fsl#")

class NIDMStat():

    def __init__(self, *args, **kwargs):
        # Keep track of the number of coordinateSpace entity already generated
        # FIXME: Merge coordinateSpace entities if identical?
        # FIXME: Use actual URIs instead
        self.coordinateSpaceId = 1

        g = ProvBundle()
        g.add_namespace("neurolex", "http://neurolex.org/wiki/")
        g.add_namespace(FSL)
        g.add_namespace(NIDM)
        g.add_namespace(NIIRI)
        g.add_namespace(CRYPTO)

        g.agent(NIIRI['software_id'], other_attributes=( 
            (PROV['type'], NIDM['Fsl']), 
            (PROV['type'], PROV['SoftwareAgent']),
            (PROV['label'],'FSL'),
            # FIXME find FSL software version
            (NIDM['softwareVersion'],'TODO') ))
        
       
        # FIXME: Check one-tailed or two-tailed test and get test type from data
        # FIXME: We want to be able to add for than one inference activity for on graph -> create a function for that
        
        
        
        
        # # FIXME: is this really empty? If so, should be deleted
        # g.entity(NIIRI['stat_image_properties_id'], other_attributes=( 
        #     (PROV['type'], FSL['statisticImageProperties']), 
        #     (PROV['label'], 'Statistical image properties')))
        
        
        self.provBundle = g
        
    def create_thresholds(self, *args, **kwargs):
        voxelThreshold = kwargs.pop('voxelThreshold')
        voxelPUncorr = kwargs.pop('voxelPUncorr')
        voxelPCorr = kwargs.pop('voxelPCorr')
        threshDesc = ""
        if not voxelThreshold is None:
            threshDesc = "Z>"+str(voxelThreshold)
            userSpecifiedThresholdType = NIDM['nidm:zStatistic']
        elif not voxelPUncorr is None:
            threshDesc = "p<"+str(voxelPUncorr)+" uncorr."
            userSpecifiedThresholdType = NIDM['nidm:pValueUncorrected']
        elif not voxelPCorr is None:
            threshDesc = "p<"+str(voxelPCorr)+" (GRF)"
            userSpecifiedThresholdType = NIDM['nidm:pValueFWER']

        # FIXME: Do we want to calculate an uncorrected p equivalent to the Z thresh? 
        # FIXME: Do we want/Can we find a corrected p equivalent to the Z thresh? 
        heightThreshAllFields = {
            PROV['type']: NIDM['heightThreshold'], PROV['label']: "Height Threshold: "+threshDesc,
            NIDM['userSpecifiedThresholdType']: userSpecifiedThresholdType , PROV['value']: voxelThreshold,
            NIDM['pValueUncorrected']: voxelPUncorr, NIDM['pValueFWER']: voxelPCorr
            }
        self.provBundle.entity(NIIRI['height_threshold_id'], other_attributes=dict((k,v) for k,v in heightThreshAllFields.iteritems() if v is not None))

        extent = kwargs.pop('extent')
        extentPUncorr = kwargs.pop('extentPUncorr')
        extentPCorr = kwargs.pop('extentPCorr')
        threshDesc = ""
        if not extent is None:
            threshDesc = "k>"+str(extent)
        elif not extentPUncorr is None:
            threshDesc = "p<"+str(extentPUncorr)+" uncorr."
        elif not extentPCorr is None:
            threshDesc = "p<"+str(extentPCorr)+" corr."
        exentThreshAllFields = {
            PROV['type']: NIDM['extentThreshold'], PROV['label']: "Extent Threshold: "+threshDesc, NIDM['clusterSizeInVoxels']: extent,
            NIDM['pValueUncorrected']: extentPUncorr, NIDM['pValueFWER']: extentPCorr
        }
        self.provBundle.entity(NIIRI['extent_threshold_id'], other_attributes=dict((k,v) for k,v in exentThreshAllFields.iteritems() if v is not None))

    def create_cluster(self, *args, **kwargs):
        clusterIndex = kwargs.pop('id')
        statNum = int(kwargs.pop('statNum'))

        # FIXME deal with multiple contrasts
        clusterId = clusterIndex

        self.provBundle.entity(NIIRI['cluster_000'+str(clusterId)], other_attributes=( 
                             (PROV['type'] , NIDM['clusterLevelStatistic']), 
                             (PROV['label'], "Cluster Level Statistic: 000"+str(clusterId)),
                             (NIDM['clusterSizeInVoxels'], kwargs.pop('size')),
                             (NIDM['pValueFWER'], kwargs.pop('pFWER') )))
        self.provBundle.wasDerivedFrom(NIIRI['cluster_000'+str(clusterId)], NIIRI['excursion_set_id_'+str(statNum)])

        self.provBundle.entity(NIIRI['coordinate_'+str(clusterId)+"00"], other_attributes=( 
            (PROV['type'] , PROV['location']), 
            (PROV['type'] , NIDM['coordinate']),
            (NIDM['coordinateSystem'] , NIDM['mni']),
            (NIDM['coordinate1'] , str(kwargs.pop('COG1'))),
            (NIDM['coordinate2'] , str(kwargs.pop('COG2'))),
            (NIDM['coordinate3'] , str(kwargs.pop('COG3'))),
            (NIDM['coordinateInUnits1'] , str(kwargs.pop('COG1_std'))),
            (NIDM['coordinateInUnits2'] , str(kwargs.pop('COG2_std'))),
            (NIDM['coordinateInUnits3'] , str(kwargs.pop('COG3_std')))
            ))
        self.provBundle.entity(NIIRI['centerOfGravity_'+str(clusterId)], other_attributes=( 
                     (PROV['type'] , FSL['centerOfGravity']), 
                     (PROV['label'], "Center of Gravity: "+str(clusterId)),
                     (PROV['location'] , NIIRI['coordinate_'+str(clusterId)+"00"]))   )
        self.provBundle.wasDerivedFrom(NIIRI['centerOfGravity_'+str(clusterId)], NIIRI['cluster_000'+str(clusterId)])

    def create_peak(self, *args, **kwargs):
        peakIndex = kwargs.pop('id')
        clusterIndex = kwargs.pop('clusterId')
        statNum = int(kwargs.pop('statNum'))

        # FIXME: Currently assumes less than 10 clusters per contrast
        clusterId = statNum*10+clusterIndex

        # FIXME: Currently assumes less than 100 peaks 
        peakUniqueId = '000'+str(clusterIndex)+'_'+str(peakIndex)

        self.provBundle.entity(NIIRI['coordinate_'+str(peakUniqueId)], other_attributes=( 
                    (PROV['type'] , PROV['location']), 
                    (PROV['type'] , NIDM['coordinate']),
                    (PROV['label'] , "Coordinate "+str(peakUniqueId)),
                    (NIDM['coordinate1'] , kwargs.pop('x')),
                    (NIDM['coordinate2'] , kwargs.pop('y')),
                    (NIDM['coordinate3'] , kwargs.pop('z')),
                    (NIDM['coordinate1InUnits'] , kwargs.pop('std_x')),
                    (NIDM['coordinate2InUnits'] , kwargs.pop('std_y')),
                    (NIDM['coordinate3InUnits'] , kwargs.pop('std_z'))
                    ))
        self.provBundle.entity(NIIRI['peak_'+str(peakUniqueId)], other_attributes=( 
            (PROV['type'] , NIDM['peakLevelStatistic']), 
            (NIDM['equivalentZStatistic'], kwargs.pop('equivZ')),
            (PROV['location'] , NIIRI['coordinate_'+str(peakUniqueId)]))         )
        self.provBundle.wasDerivedFrom(NIIRI['peak_'+str(peakUniqueId)], NIIRI['cluster_000'+str(clusterId)])

    def create_model_fitting(self, residualsFile):
        # FIXME: Add crypto sha

        path, filename = os.path.split(residualsFile)
        self.provBundle.entity(NIIRI['residual_mean_squares_map_id'], 
            other_attributes=( (PROV['type'],NIDM['residualMeanSquaresMap'],), 
                               (PROV['location'], Identifier("file://./stats/"+filename) ),
                               (PROV['label'],"Residual Mean Squares Map" ),
                               (NIDM['fileName'],filename ),
                               (CRYPTO['sha'],"TODO" ),
                               (NIDM['coordinateSpace'], NIIRI['coordinate_space_id_'+str(self.coordinateSpaceId)])))
        self.create_coordinate_space(residualsFile)
        self.provBundle.entity(NIIRI['design_matrix_id'], 
            other_attributes=( (PROV['type'],NIDM['designMatrix'],), 
                               (PROV['location'], Identifier("file://./design_matrix.csv"))))
        self.provBundle.activity(NIIRI['model_parameters_estimation_id'], other_attributes=( 
            (PROV['type'], NIDM['ModelParametersEstimation']),(PROV['label'], "Model Parameters Estimation")))
        self.provBundle.used(NIIRI['model_parameters_estimation_id'], NIIRI['design_matrix_id'])
        self.provBundle.wasAssociatedWith(NIIRI['model_parameters_estimation_id'], NIIRI['software_id'])
        
        self.provBundle.wasGeneratedBy(NIIRI['residual_mean_squares_map_id'], NIIRI['model_parameters_estimation_id'])

    # Generate prov for contrast map
    def create_contrast_map(self, copeFile, varCopeFile, statFile, zStatFile, contrastName, contrastNum, dof, contrastWeights):
        # Contrast id entity
        # FIXME: Get contrast weights
        self.provBundle.entity(NIIRI['contrast_id_'+contrastNum], 
            other_attributes=( (PROV['type'], NIDM['TContrast']), 
                               (PROV['label'], "T Contrast: "+contrastName), 
                               (NIDM['contrastName'], contrastName),
                               (NIDM['contrastWeights'], contrastWeights)))

        # Create related activities
        self.provBundle.activity(NIIRI['contrast_estimation_id_'+contrastNum], other_attributes=( 
            (PROV['type'], NIDM['ContrastEstimation']),
            (PROV['label'], "Contrast estimation: "+contrastName)))

        # Contrast Map entity
        path, filename = os.path.split(copeFile)
        self.provBundle.entity('niiri:'+'contrast_map_id_'+contrastNum, other_attributes=( 
            (PROV['type'], NIDM['contrastMap']), 
            (NIDM['coordinateSpace'], NIIRI['coordinate_space_id_'+str(self.coordinateSpaceId)]),
            (PROV['location'], Identifier("file://./"+filename)),
            (NIDM['fileName'], filename),
            (NIDM['contrastName'], contrastName),
            (PROV['label'], "Contrast map: "+contrastName)))
        self.create_coordinate_space(copeFile)
        self.provBundle.wasGeneratedBy(NIIRI['contrast_map_id_'+contrastNum], NIIRI['contrast_estimation_id_'+contrastNum])
        self.provBundle.wasAssociatedWith(NIIRI['contrast_estimation_id_'+contrastNum], NIIRI['software_id'])

        # Contrast Variance Map entity
        path, filename = os.path.split(varCopeFile)
        # FIXME: Standard error or contrast variance...
        self.provBundle.entity('niiri:'+'contrast_standard_error_map_id_'+contrastNum, other_attributes=( 
            (PROV['type'], NIDM['contrastStandardErrorMap']), 
            (NIDM['coordinateSpace'], NIIRI['coordinate_space_id_'+str(self.coordinateSpaceId)]),
            (PROV['location'], Identifier("file://./"+filename)),
            (NIDM['fileName'], filename),
            (PROV['label'], "Contrast variance map")))
        self.create_coordinate_space(varCopeFile)
        self.provBundle.wasGeneratedBy(NIIRI['contrast_standard_error_map_id_'+contrastNum], NIIRI['contrast_estimation_id_'+contrastNum])

        
        # FIXME: Remove TODOs
        # FIXME: Add sha sum

        # Z-Statistical Map entity
        path, filename = os.path.split(zStatFile)
        self.provBundle.entity(NIIRI['z_statistical_map_id_'+contrastNum ],
            other_attributes=(  (PROV['type'], FSL['ZStatisticalMap']), 
                                (PROV['label'], "Z-statistical Map: "+contrastName) ,
                                (PROV['location'], Identifier("file://./stats/"+filename)),
                                (NIDM['contrastName'], contrastName),
                                (NIDM['fileName'], filename),
                                (NIDM['coordinateSpace'], NIIRI['coordinate_space_id_'+str(self.coordinateSpaceId)]),
                                ) )
        self.create_coordinate_space(zStatFile)
        

        # Statistical Map entity
        path, filename = os.path.split(statFile)
        self.provBundle.entity(NIIRI['statistical_map_id_'+contrastNum ],
            other_attributes=(  (PROV['type'], NIDM['statisticalMap']), 
                                (PROV['label'], "Statistical Map: "+contrastName) ,
                                (PROV['location'], Identifier("file://./stats/"+filename)),
                                (NIDM['fileName'], filename),
                                (NIDM['statisticType'], NIDM['tStatisticTODO']),
                                (NIDM['errorDegreesOfFreedom'], dof),
                                (NIDM['effectDegreesOfFreedom'], 'TODO'),
                                (NIDM['coordinateSpace'], NIIRI['coordinate_space_id_'+str(self.coordinateSpaceId)]),
                                ) )
        self.create_coordinate_space(statFile)
        self.provBundle.wasGeneratedBy(NIIRI['statistical_map_id_'+contrastNum], NIIRI['contrast_estimation_id_'+contrastNum])
               
        self.provBundle.wasGeneratedBy(NIIRI['z_statistical_map_id_'+contrastNum], NIIRI['contrast_estimation_id_'+contrastNum])
        self.provBundle.used(NIIRI['contrast_estimation_id_'+contrastNum], NIIRI['residual_mean_squares_map_id'])
        self.provBundle.used(NIIRI['contrast_estimation_id_'+contrastNum], NIIRI['design_matrix_id'])
        self.provBundle.used(NIIRI['contrast_estimation_id_'+contrastNum], NIIRI['contrast_id_'+contrastNum])


        # In FSL we have a single thresholding (extent, height) applied to all contrasts 
        self.provBundle.activity(NIIRI['inference_id_'+contrastNum], 
            other_attributes=( (PROV['type'], NIDM['inference']), 
                               (PROV['label'] , "Inference: "+contrastName), 
                               (NIDM['statisticalTest'] , NIDM['oneTailedTtest'])))
        self.provBundle.used(NIIRI['inference_id_'+contrastNum], NIIRI['height_threshold_id'])
        self.provBundle.used(NIIRI['inference_id_'+contrastNum], NIIRI['extent_threshold_id'])
        self.provBundle.used(NIIRI['inference_id_'+contrastNum], NIIRI['z_statistical_map_id_'+contrastNum])

        self.provBundle.wasAssociatedWith(NIIRI['inference_id_'+contrastNum], NIIRI['software_id'])

        self.provBundle.wasGeneratedBy(NIIRI['search_space_id'], NIIRI['inference_id_'+contrastNum])
        # self.provBundle.wasGeneratedBy(NIIRI['stat_image_properties_id'], NIIRI['inference_id_'+contrastNum])

    # Generate prov for a coordinate space entity 
    def create_coordinate_space(self, niftiFile):
        thresImg = nib.load(niftiFile)
        thresImgHdr = thresImg.get_header()

        numDim = len(thresImg.shape)

        mydict = { 
            PROV['type']: NIDM['coordinateSpace'], 
            NIDM['dimensions']: str(thresImg.shape).replace('(', '[').replace(')', ']'),
            NIDM['numberOfDimensions']: numDim,
            NIDM['voxelToWorldMapping']: '%s'%', '.join(str(thresImg.get_qform()).strip('()').replace('. ', '').split()).replace('[,', '[').replace('\n', ''),
            # FIXME: How to get the coordinate system? default for FSL?
            NIDM['coordinateSystem']: NIDM['mniCoordinateSystem'],           
            # FIXME: this gives mm, sec => what is wrong, FSL file or nibabel?
            # NIDM['voxelUnits']: '[%s]'%str(thresImgHdr.get_xyzt_units()).strip('()'),
            NIDM['voxelUnits']: "['mm', 'mm', 'mm']",
            NIDM['voxelSize']: '[%s]'%', '.join(map(str, thresImgHdr['pixdim'][1:(numDim+1)])),
            PROV['label']: "Coordinate space "+str(self.coordinateSpaceId)}

        self.provBundle.entity(NIIRI['coordinate_space_id_'+str(self.coordinateSpaceId)], other_attributes=mydict)
        self.coordinateSpaceId = self.coordinateSpaceId + 1

    # Generate prov for search space entity generated by the inference activity
    def create_search_space(self, searchSpaceFile, searchVolume, reselSizeInVoxels):
        path, filename = os.path.split(searchSpaceFile)

        self.provBundle.entity(NIIRI['search_space_id'], other_attributes=( 
                (PROV['label'], "Search Space"), 
                (PROV['type'], NIDM['mask']), 
                (PROV['location'], Identifier("file://./"+filename)),
                (NIDM['coordinateSpace'], NIIRI['coordinate_space_id_'+str(self.coordinateSpaceId)]),
                (NIDM['searchVolumeInVoxels'], searchVolume),
                (FSL['reselSizeInVoxels'], reselSizeInVoxels)))
        self.create_coordinate_space(searchSpaceFile)
        

    def create_excursion_set(self, excusionSetFile, statNum, underlayFile):
        zFileImg = excusionSetFile
        path, filename = os.path.split(zFileImg)

        path, underlay_filename = os.path.split(underlayFile)

        self.provBundle.entity(NIIRI['excursion_set_id_'+str(statNum)], other_attributes=( 
            (PROV['type'], NIDM['excursionSet']), 
            (PROV['location'], Identifier("file://./"+filename)),
            (NIDM['fileName'], filename),
            (NIDM['underlayFile'], Identifier("file://./"+underlay_filename)),
            (NIDM['coordinateSpace'], NIIRI['coordinate_space_id_'+str(self.coordinateSpaceId)]),
            (PROV['label'], "Excursion Set"),
            ))
        self.provBundle.wasGeneratedBy(NIIRI['excursion_set_id_'+str(statNum)], NIIRI['inference_id_'+str(statNum)])
        self.create_coordinate_space(zFileImg)

    def save_prov_to_files(self, showattributes=False):
        suffixName = ''
        if showattributes is False:
            suffixName = '_without_attributes'

        jsondata = self.provBundle.get_provjson(indent=4)
        JSONfile = open('./FSL_example.json', 'w');
        JSONfile.write(jsondata)
        PROVNfile = open('./FSL_example.provn', 'w');
        PROVNfile.write(self.provBundle.get_provn(4))

        dot = graph.prov_to_dot(self.provBundle, use_labels=True, show_element_attributes=showattributes)
        dot.set_dpi(200)
        dot.write_png('./FSL_example'+suffixName+'.png')

