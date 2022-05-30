#%%

import ModelTraining.Preprocessing.FeatureCreation.add_features as feat_utils
import ModelTraining.Preprocessing.get_data_and_feature_set
import ModelTraining.Preprocessing.data_analysis as data_analysis
import ModelTraining.Training.TrainingUtilities.training_utils as train_utils
import ModelTraining.Preprocessing.DataImport.data_import as data_import
import ModelTraining.Utilities.Plotting.plot_distributions_spectra as plt_dist
import os
import numpy as np
import pandas as pd
from ModelTraining.datamodels.datamodels.processing.datascaler import Normalizer


if __name__ == '__main__':
    #%%
    root_dir = "../"
    data_dir = "../../"
    # Added: Preprocessing - Smooth features
    usecase_config_path = os.path.join(root_dir, 'Configuration/UseCaseConfig')
    list_usecases = ['CPS-Data', 'SensorA6', 'SensorB2', 'SensorC6', 'Solarhouse1','Solarhouse2']

    dict_usecases = [data_import.load_from_json(os.path.join(usecase_config_path, f"{name}.json")) for name in
                     list_usecases]

    interaction_only=True
    matrix_path = "./Figures/Correlation"
    vif_path = './Figures/Correlation/VIF'
    os.makedirs(vif_path, exist_ok=True)
    float_format="%.2f"
    expander_parameters = {'degree': 2, 'interaction_only': True, 'include_bias': False}


    #%%
    ##### Square root transformation
    density_dir ="./Figures/Density"
    os.makedirs(density_dir, exist_ok=True)

    for dict_usecase in dict_usecases:
        usecase_name = dict_usecase['name']
        density_dir_usecase = os.path.join(density_dir, usecase_name)
        os.makedirs(density_dir_usecase, exist_ok=True)

        # Get data and feature set
        data, feature_set = ModelTraining.Preprocessing.get_data_and_feature_set.get_data_and_feature_set(
            os.path.join(data_dir, dict_usecase['dataset']),
            os.path.join(root_dir, dict_usecase['fmu_interface']))
        data, feature_set = feat_utils.add_features(data, feature_set, dict_usecase)
        data = data.astype('float')
        # Data preprocessing
        #data = dp_utils.preprocess_data(data, dict_usecase['to_smoothe'], do_smoothe=True)

        feats_for_density = [feature.name for feature in feature_set.get_input_feats() if
                             not feature.cyclic and not feature.statistical]
        if usecase_name in ['CPS-Data', 'SensorA6', 'SensorB2', 'SensorC6']:
            feats_for_density.remove("holiday_weekend")
            feats_for_density.remove('daylight')
        if usecase_name == 'Solarhouse1':
            feats_for_density.remove('VDSolar_inv')
        if usecase_name == 'Solarhouse1':
            data['SGlobal'][data['SGlobal'] < 30] = 0

        feats_for_density_full = feats_for_density + feature_set.get_output_feature_names()

        scaler = Normalizer()
        scaler.fit(data)
        data = scaler.transform(data)

        output_dir = os.path.join(density_dir_usecase, 'SqrtTransformation')
        os.makedirs(output_dir, exist_ok=True)
        vals_sqrt_full = np.sqrt(data[feats_for_density_full])
        plt_dist.plot_density(vals_sqrt_full[feats_for_density], output_dir, f'Density - {usecase_name} - Square Root Transformation - nonzero samples',
                              omit_zero_samples=True, store_tikz=False)
        plt_dist.plot_density(vals_sqrt_full, output_dir, f'Density - {usecase_name} - Square Root Transformation - full - nonzero samples',
                              omit_zero_samples=True, store_tikz=False)
        for feature in feats_for_density_full:
            plt_dist.plot_qq(vals_sqrt_full[feature], output_dir, f'QQ - {usecase_name} - {feature} - Box-cox - nonzero samples')

        df_skew = data_analysis.calc_skew_kurtosis(vals_sqrt_full)
        df_skew_nonzero = data_analysis.calc_skew_kurtosis(vals_sqrt_full, True)
        df_skew.to_csv(os.path.join(output_dir, f"{usecase_name}_sqrt_skew_kurtosis.csv"), index_label='Metric')
        df_skew_nonzero.to_csv(os.path.join(output_dir, f"{usecase_name}_sqrt_skew_kurtosis_nonzero.csv"),
                               index_label='Metric')

    #%%
    ##### Box-cox transformation
    density_dir ="./Figures/Density"
    os.makedirs(density_dir, exist_ok=True)

    for dict_usecase in dict_usecases:
        usecase_name = dict_usecase['name']
        density_dir_usecase = os.path.join(density_dir, usecase_name)
        os.makedirs(density_dir_usecase, exist_ok=True)

        # Get data and feature set
        data, feature_set = ModelTraining.Preprocessing.get_data_and_feature_set.get_data_and_feature_set(
            os.path.join(data_dir, dict_usecase['dataset']),
            os.path.join(root_dir, dict_usecase['fmu_interface']))
        data, feature_set = feat_utils.add_features(data, feature_set, dict_usecase)
        data = data.astype('float')
        # Data preprocessing
        #data = dp_utils.preprocess_data(data, dict_usecase['to_smoothe'], do_smoothe=True)

        feats_for_density = [feature.name for feature in feature_set.get_input_feats() if
                             not feature.cyclic and not feature.statistical]
        if usecase_name in ['CPS-Data', 'SensorA6', 'SensorB2', 'SensorC6']:
            feats_for_density.remove("holiday_weekend")
            feats_for_density.remove('daylight')
        if usecase_name == 'Solarhouse1':
            feats_for_density.remove('VDSolar_inv')
        if usecase_name == 'Solarhouse1':
            data['SGlobal'][data['SGlobal'] < 30] = 0

        feats_for_density_full = feats_for_density + feature_set.get_output_feature_names()

        scaler = Normalizer()
        scaler.fit(data)
        data = scaler.transform(data)

        output_dir = os.path.join(density_dir_usecase, 'Box-coxTransformation')
        os.makedirs(output_dir, exist_ok=True)
        boxcox_df = data_analysis.boxcox_transf(data[feats_for_density_full])
        plt_dist.plot_density(boxcox_df[feats_for_density], output_dir,
                              f'Density - {usecase_name} - Box-cox Transformation - nonzero samples',
                              omit_zero_samples=True, store_tikz=False)
        plt_dist.plot_density(boxcox_df, output_dir,
                              f'Density - {usecase_name} - Box-cox Transformation - full - nonzero samples',
                              omit_zero_samples=True, store_tikz=False)
        for feature in feats_for_density_full:
            plt_dist.plot_qq(boxcox_df[feature], output_dir, f'QQ - {usecase_name} - {feature} - Box-cox - nonzero samples')

        df_skew = data_analysis.calc_skew_kurtosis(boxcox_df)
        df_skew_nonzero = data_analysis.calc_skew_kurtosis(boxcox_df, True)
        df_skew.to_csv(os.path.join(output_dir, f"{usecase_name}_boxcox_skew_kurtosis.csv"), index_label='Metric')
        df_skew_nonzero.to_csv(os.path.join(output_dir, f"{usecase_name}_boxcox_skew_kurtosis_nonzero.csv"),
                               index_label='Metric')

    #%% Skew and kurtosis
    density_dir = "./Figures/Density"
    os.makedirs(density_dir, exist_ok=True)

    for dict_usecase in dict_usecases:
        usecase_name = dict_usecase['name']
        density_dir_usecase = os.path.join(density_dir, usecase_name)
        os.makedirs(density_dir_usecase, exist_ok=True)
        # Get data and feature set
        data, feature_set = ModelTraining.Preprocessing.get_data_and_feature_set.get_data_and_feature_set(
            os.path.join(data_dir, dict_usecase['dataset']),
            os.path.join(root_dir, dict_usecase['fmu_interface']))
        data, feature_set = feat_utils.add_features(data, feature_set, dict_usecase)
        data = data.astype('float')
        # Data preprocessing
        # data = dp_utils.preprocess_data(data, dict_usecase['to_smoothe'], do_smoothe=True)

        feats_for_density = [feature.name for feature in feature_set.get_input_feats() if
                             not feature.cyclic and not feature.statistical]
        if usecase_name in ['CPS-Data', 'SensorA6', 'SensorB2', 'SensorC6']:
            feats_for_density.remove("holiday_weekend")
            feats_for_density.remove('daylight')
        if usecase_name == 'Solarhouse1':
            feats_for_density.remove('VDSolar_inv')
        if usecase_name == 'Solarhouse1':
            data['SGlobal'][data['SGlobal'] < 30] = 0

        feats_for_density_full = feats_for_density + feature_set.get_output_feature_names()

        scaler = Normalizer()
        scaler.fit(data)
        data = scaler.transform(data)

        df_skew = data_analysis.calc_skew_kurtosis(data[feats_for_density_full])
        df_skew_nonzero = data_analysis.calc_skew_kurtosis(data[feats_for_density_full], True)
        df_skew.to_csv(os.path.join(density_dir_usecase, f"{usecase_name}_skew_kurtosis.csv"), index_label='Metric')
        df_skew_nonzero.to_csv(os.path.join(density_dir_usecase, f"{usecase_name}_skew_kurtosis_nonzero.csv"), index_label='Metric')