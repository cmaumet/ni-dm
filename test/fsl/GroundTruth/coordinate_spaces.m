% Convenience function to write out coordinate space entities in FSL ground
% truth
function coordinate_spaces(featDir)
    coordinate_space_entity(fullfile(featDir, 'stats', 'sigmasquareds.nii.gz'), 1, true);
    coordinate_space_entity(fullfile(featDir, 'mask.nii.gz'), 2, true);
    coordinate_space_entity(fullfile(featDir, 'stats', 'cope1.nii.gz'), 3, true);
    coordinate_space_entity(fullfile(featDir, 'stats', 'varcope1.nii.gz'), 4, true);
    coordinate_space_entity(fullfile(featDir, 'stats', 'zstat1.nii.gz'), 5, true);
    coordinate_space_entity(fullfile(featDir, 'stats', 'tstat1.nii.gz'), 6, true);
    coordinate_space_entity(fullfile(featDir, 'thresh_zstat1.nii.gz'), 7, true);
end