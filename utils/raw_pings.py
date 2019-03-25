from helpers import *
import pyspark.sql.functions as F
import pandas as pd
from pyspark.sql import SQLContext

spark = get_spark()

def get_page_load_times(df):
    """
    Function to aggreagte raw pings by addon_id and get average page load time
    :param df: raw pings dataframe
    :return: aggregated dataframe
    """
    hist = "FX_PAGE_LOAD_MS_2"

    avg_page_load = (
      df
      .filter(lambda x: hist in x['payload']['histograms'].keys())
      .flatMap(lambda x: [(item,histogram_mean(x['payload']['histograms'][hist]['values']))
                          for item in x['environment']['addons']['activeAddons'].keys()])
    )

    schema = StructType([StructField('addon_id', StringType(), True),
                         StructField('avg_page_loadtime', FloatType(), True)])

    avg_page_load_df = spark.createDataFrame(data=avg_page_load, schema=schema)

    avg_page_load_agg = (
      avg_page_load_df
      .groupBy("addon_id")
      .agg(F.mean("avg_page_loadtime"))
      .withColumnRenamed("avg(avg_page_loadtime)", "avg_page_load_time")
    )
    return avg_page_load_agg


def get_tab_switch_time(df):
    """
    :param df: raw pings
    :return:
    """

    tab_switch_hist = (
        df
        .filter(lambda x: 'environment' in x.keys())
        .filter(lambda x: 'addons' in x['environment'].keys())
        .filter(lambda x: 'activeAddons' in x['environment']['addons'])
        .filter(lambda x: 'payload' in x.keys())
        .filter(lambda x: 'histograms' in x['payload'].keys())
        .filter(lambda x: 'FX_TAB_SWITCH_TOTAL_E10S_MS' in x['payload']['histograms'].keys())
        .map(lambda x: (x['environment']['addons']['activeAddons'].keys(),
                        x['payload']['histograms']['FX_TAB_SWITCH_TOTAL_E10S_MS']))
        .map(lambda x: [(i, x[1]) for i in x[0]])
        .flatMap(lambda x: x))

    tab_switch = tab_switch_hist.map(lambda x: (x[0], histogram_mean(x[1]['values'])))

    tab_switch_df = (
        spark.createDataFrame(tab_switch, ['addon_id', 'tab_switch_ms'])
        .groupby('addon_id')
        .agg(F.mean('tab_switch_ms').alias('tab_switch_ms')))

    return tab_switch_df

##########################
# storage local 'get' time
##########################


def get_storage_local_get_time():

    storage_local_get_df = get_hist_avg('WEBEXT_STORAGE_LOCAL_GET_MS_BY_ADDONID', just_keyed_hist)

    storage_local_get_by_addon = (
        storage_local_get_df
        .groupBy('addon_id')
        .agg(F.mean('avg_webext_storage_local_get_ms_by_addonid').alias('avg_storage_local_get_ms'))
    )
    return storage_local_get_by_addon

##########################
# storage local 'set' time
##########################


def get_storage_local_set_time():
    storage_local_set_df = get_hist_avg('WEBEXT_STORAGE_LOCAL_SET_MS_BY_ADDONID', just_keyed_hist)

    storage_local_set_by_addon = (
        storage_local_set_df
        .groupBy('addon_id')
        .agg(F.mean('avg_webext_storage_local_get_ms_by_addonid').alias('avg_storage_local_get_ms'))
    )
    return storage_local_set_by_addon


##############
# startup time
##############


def get_startup_time():
    hist = "WEBEXT_EXTENSION_STARTUP_MS_BY_ADDONID"

    ext_startup_df = get_hist_avg(hist)

    startup_time_by_addon = (
      ext_startup_df
      .groupBy("addon_id")
      .agg(F.mean("avg_WEBEXT_EXTENSION_STARTUP_MS_BY_ADDONID"))
      .withColumnRenamed("avg(avg_WEBEXT_EXTENSION_STARTUP_MS_BY_ADDONID)","avg_startup_time")
    )
    return startup_time_by_addon


###########################
# background page load time
###########################

def get_bkgd_load_time():

    hist = "WEBEXT_BACKGROUND_PAGE_LOAD_MS_BY_ADDONID"
    return get_hist_avg(hist)

#################################
# browser action pop up load time
#################################

def get_ba_popup_load_time():

    hist = "WEBEXT_BROWSERACTION_POPUP_OPEN_MS_BY_ADDONID"

    ba_popup_load_time_df = get_hist_avg(hist)

    ba_popup_load_time_by_addon = (
      ba_popup_load_time_df
      .groupBy("addon_id")
      .agg(F.mean("avg_WEBEXT_BROWSERACTION_POPUP_OPEN_MS_BY_ADDONID"))
      .withColumnRenamed("avg(avg_WEBEXT_BROWSERACTION_POPUP_OPEN_MS_BY_ADDONID)","avg_ba_popup_load_time")
    )

    return ba_popup_load_time_by_addon

##############################
# page action pop up load time
##############################


def get_pa_popup_load_time():
    hist = "WEBEXT_PAGEACTION_POPUP_OPEN_MS_BY_ADDONID"

    pa_popup_load_time_df = get_hist_avg(hist)

    pa_popup_load_time_by_addon = (
      pa_popup_load_time_df
      .groupBy("addon_id")
      .agg(F.mean("avg_WEBEXT_BROWSERACTION_POPUP_OPEN_MS_BY_ADDONID"))
      .withColumnRenamed("avg(avg_WEBEXT_BROWSERACTION_POPUP_OPEN_MS_BY_ADDONID)","avg_ba_popup_load_time")
    )
    return pa_popup_load_time_by_addon

###############################
# content script injection time
###############################


def get_cs_injection_time():
    hist = 'WEBEXT_CONTENT_SCRIPT_INJECTION_MS_BY_ADDONID'
    content_script_time_df = get_hist_avg(hist)

    content_script_time_by_addon = (
      content_script_time_df
      .groupBy("addon_id")
      .agg(F.mean("avg_WEBEXT_CONTENT_SCRIPT_INJECTION_MS_BY_ADDONID").alias('avg_content_script_injection_ms'))
    )
    return content_script_time_by_addon
