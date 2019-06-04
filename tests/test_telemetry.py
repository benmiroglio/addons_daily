from addons_daily.utils.telemetry_data import *
from addons_daily.addons_report import expand_addons
from addons_daily.utils.helpers import is_same
from pyspark.sql.types import *
from pyspark.sql import Row
import pytest
import json
import os


BASE_DATE = "20190515"


def df_to_json(df):
    return [i.asDict() for i in df.collect()]


def load_test_data(prefix, spark):
    root = os.path.dirname(__file__)
    schema_path = os.path.join(root, "resources", "{}_schema.json".format(prefix))
    with open(schema_path) as f:
        d = json.load(f)
        schema = StructType.fromJson(d)
    rows_path = os.path.join(root, "resources", "{}.json".format(prefix))
    # FAILFAST causes us to abort early if the data doesn't match
    # the given schema. Without this there was as very annoying
    # problem where dataframe.collect() would return an empty set.
    frame = spark.read.json(rows_path, schema, mode="FAILFAST")
    return frame


@pytest.fixture()
def spark():
    spark_session = SparkSession.builder.appName("addons_daily_tests").getOrCreate()
    return spark_session


@pytest.fixture()
def main_summary(spark):
    return load_test_data("main_summary", spark)


@pytest.fixture()
def events(spark):
    return load_test_data("events", spark)


@pytest.fixture()
def search_clients_daily(spark):
    return load_test_data("search_clients_daily", spark).filter(
        "submission_date_s3 = '{}'".format(BASE_DATE)
    )


@pytest.fixture()
def addons_expanded(main_summary):
    return expand_addons(main_summary)


@pytest.fixture()
def main_summary_day(main_summary):
    return main_summary.filter("submission_date_s3 = '{}'".format(BASE_DATE))


@pytest.fixture()
def addons_expanded_day(addons_expanded):
    return addons_expanded.filter("submission_date_s3 = '{}'".format(BASE_DATE))


def test_addon_names(addons_expanded_day, spark):
    output = df_to_json(get_top_addon_names(addons_expanded_day))
    expected = [
        {
            "addon_id": u"baidu-code-update@mozillaonline.com",
            "name": u"Baidu Search Update",
        },
        {"addon_id": u"screenshots@mozilla.org", "name": u"Firefox Screenshots"},
        {"addon_id": u"non-system-addon1", "name": u"Non systemn Addon 1"},
        {
            "addon_id": u"hotfix-update-xpi-intermediate@mozilla.com",
            "name": u"hotfix-update-xpi-intermediate",
        },
        {"addon_id": u"fxmonitor@mozilla.org", "name": u"Firefox Monitor"},
        {"addon_id": u"non-system-addon2", "name": u"Non System Addon 2"},
        {"addon_id": u"formautofill@mozilla.org", "name": u"Form Autofill"},
        {"addon_id": u"webcompat@mozilla.org", "name": u"Web Compat"},
    ]
    assert output == expected


def test_browser_metrics(addons_expanded_day, spark):
    """
    Given a dataframe of some actual sampled data, ensure that
    the get_pct_tracking_enabled outputs the correct dataframe
    :param addons_expanded: pytest fixture defined above
    :return: assertion whether the expected output indeed matches the true output
    """
    output = df_to_json(get_browser_metrics(addons_expanded_day))
    expected = [
        {
            "addon_id": u"baidu-code-update@mozillaonline.com",
            "avg_bookmarks": None,
            "avg_tabs": None,
            "avg_toolbox_opened_count": None,
            "avg_uri": 33.0,
            "pct_w_tracking_prot_enabled": 0.0,
        },
        {
            "addon_id": u"screenshots@mozilla.org",
            "avg_bookmarks": None,
            "avg_tabs": None,
            "avg_toolbox_opened_count": None,
            "avg_uri": 33.0,
            "pct_w_tracking_prot_enabled": 0.0,
        },
        {
            "addon_id": u"non-system-addon1",
            "avg_bookmarks": None,
            "avg_tabs": None,
            "avg_toolbox_opened_count": None,
            "avg_uri": 33.0,
            "pct_w_tracking_prot_enabled": 0.0,
        },
        {
            "addon_id": u"hotfix-update-xpi-intermediate@mozilla.com",
            "avg_bookmarks": None,
            "avg_tabs": None,
            "avg_toolbox_opened_count": None,
            "avg_uri": 33.0,
            "pct_w_tracking_prot_enabled": 0.0,
        },
        {
            "addon_id": u"fxmonitor@mozilla.org",
            "avg_bookmarks": None,
            "avg_tabs": None,
            "avg_toolbox_opened_count": None,
            "avg_uri": 33.0,
            "pct_w_tracking_prot_enabled": 0.0,
        },
        {
            "addon_id": u"non-system-addon2",
            "avg_bookmarks": None,
            "avg_tabs": None,
            "avg_toolbox_opened_count": None,
            "avg_uri": 33.0,
            "pct_w_tracking_prot_enabled": 0.0,
        },
        {
            "addon_id": u"formautofill@mozilla.org",
            "avg_bookmarks": None,
            "avg_tabs": None,
            "avg_toolbox_opened_count": None,
            "avg_uri": 33.0,
            "pct_w_tracking_prot_enabled": 0.0,
        },
        {
            "addon_id": u"webcompat@mozilla.org",
            "avg_bookmarks": None,
            "avg_tabs": None,
            "avg_toolbox_opened_count": None,
            "avg_uri": 33.0,
            "pct_w_tracking_prot_enabled": 0.0,
        },
    ]
    assert output == expected


def test_user_demo_metrics(addons_expanded_day, spark):
    output = df_to_json(get_user_demo_metrics(addons_expanded_day))
    expected = [
        {
            "addon_id": u"baidu-code-update@mozillaonline.com",
            "country_dist": {u"GB": 1.0},
            "os_dist": {u"Windows_NT": 1.0},
        },
        {
            "addon_id": u"screenshots@mozilla.org",
            "country_dist": {u"GB": 1.0},
            "os_dist": {u"Windows_NT": 1.0},
        },
        {
            "addon_id": u"non-system-addon1",
            "country_dist": {u"GB": 1.0},
            "os_dist": {u"Windows_NT": 1.0},
        },
        {
            "addon_id": u"hotfix-update-xpi-intermediate@mozilla.com",
            "country_dist": {u"GB": 1.0},
            "os_dist": {u"Windows_NT": 1.0},
        },
        {
            "addon_id": u"fxmonitor@mozilla.org",
            "country_dist": {u"GB": 1.0},
            "os_dist": {u"Windows_NT": 1.0},
        },
        {
            "addon_id": u"non-system-addon2",
            "country_dist": {u"GB": 1.0},
            "os_dist": {u"Windows_NT": 1.0},
        },
        {
            "addon_id": u"formautofill@mozilla.org",
            "country_dist": {u"GB": 1.0},
            "os_dist": {u"Windows_NT": 1.0},
        },
        {
            "addon_id": u"webcompat@mozilla.org",
            "country_dist": {u"GB": 1.0},
            "os_dist": {u"Windows_NT": 1.0},
        },
    ]
    print("output", output)
    print("expected", expected)
    assert output == expected


def test_trend_metrics(addons_expanded, spark):
    output = df_to_json(get_trend_metrics(addons_expanded, BASE_DATE))
    expected_output = [
        {
            "addon_id": "baidu-code-update@mozillaonline.com",
            "mau": 1,
            "wau": 1,
            "dau": 1,
            "dau_prop": 1.0,
        },
        {
            "addon_id": "tls13-version-fallback-rollout-bug1462099@mozilla.org",
            "mau": 1,
            "wau": None,
            "dau": None,
            "dau_prop": None,
        },
        {
            "addon_id": "screenshots@mozilla.org",
            "mau": 2,
            "wau": 1,
            "dau": 1,
            "dau_prop": 1.0,
        },
        {
            "addon_id": "non-system-addon1",
            "mau": 1,
            "wau": 1,
            "dau": 1,
            "dau_prop": 1.0,
        },
        {
            "addon_id": "firefox@getpocket.com",
            "mau": 1,
            "wau": None,
            "dau": None,
            "dau_prop": None,
        },
        {
            "addon_id": "hotfix-update-xpi-intermediate@mozilla.com",
            "mau": 1,
            "wau": 1,
            "dau": 1,
            "dau_prop": 1.0,
        },
        {
            "addon_id": "fxmonitor@mozilla.org",
            "mau": 1,
            "wau": 1,
            "dau": 1,
            "dau_prop": 1.0,
        },
        {
            "addon_id": "aushelper@mozilla.org",
            "mau": 1,
            "wau": None,
            "dau": None,
            "dau_prop": None,
        },
        {
            "addon_id": "onboarding@mozilla.org",
            "mau": 1,
            "wau": None,
            "dau": None,
            "dau_prop": None,
        },
        {
            "addon_id": "activity-stream@mozilla.org",
            "mau": 1,
            "wau": None,
            "dau": None,
            "dau_prop": None,
        },
        {
            "addon_id": "non-system-addon2",
            "mau": 1,
            "wau": 1,
            "dau": 1,
            "dau_prop": 1.0,
        },
        {
            "addon_id": "followonsearch@mozilla.com",
            "mau": 1,
            "wau": None,
            "dau": None,
            "dau_prop": None,
        },
        {
            "addon_id": "formautofill@mozilla.org",
            "mau": 2,
            "wau": 1,
            "dau": 1,
            "dau_prop": 1.0,
        },
        {
            "addon_id": "webcompat@mozilla.org",
            "mau": 2,
            "wau": 1,
            "dau": 1,
            "dau_prop": 1.0,
        },
    ]

    assert output == expected_output


def test_top_ten_coinstalls(addons_expanded_day, spark):
    """
    Given a dataframe of some actual sampled data, ensure that
    the get_pct_tracking_enabled outputs the correct dataframe
    :param main_summary_tto: pytest fixture defined above, sample data from main_summary
    :return: assertion whether the expected output indeed matches the true output
    """
    output = df_to_json(get_top_10_coinstalls(addons_expanded_day))
    expected = [
        {
            "addon_id": u"baidu-code-update@mozillaonline.com",
            "top_10_coinstalls": {
                u"0": u"non-system-addon2",
                u"1": u"non-system-addon1",
            },
        },
        {
            "addon_id": u"screenshots@mozilla.org",
            "top_10_coinstalls": {
                u"0": u"hotfix-update-xpi-intermediate@mozilla.com",
                u"1": u"non-system-addon1",
            },
        },
        {
            "addon_id": u"non-system-addon1",
            "top_10_coinstalls": {
                u"0": u"non-system-addon1",
                u"1": u"non-system-addon2",
            },
        },
        {
            "addon_id": u"hotfix-update-xpi-intermediate@mozilla.com",
            "top_10_coinstalls": {
                u"0": u"non-system-addon1",
                u"1": u"non-system-addon2",
            },
        },
        {
            "addon_id": u"fxmonitor@mozilla.org",
            "top_10_coinstalls": {
                u"0": u"non-system-addon1",
                u"1": u"hotfix-update-xpi-intermediate@mozilla.com",
            },
        },
        {
            "addon_id": u"non-system-addon2",
            "top_10_coinstalls": {
                u"0": u"non-system-addon2",
                u"1": u"non-system-addon1",
            },
        },
        {
            "addon_id": u"formautofill@mozilla.org",
            "top_10_coinstalls": {
                u"0": u"non-system-addon1",
                u"1": u"non-system-addon2",
            },
        },
        {
            "addon_id": u"webcompat@mozilla.org",
            "top_10_coinstalls": {
                u"0": u"non-system-addon1",
                u"1": u"non-system-addon2",
            },
        },
    ]


def test_engagement_metrics(addons_expanded_day, main_summary_day, spark):
    """
    Given a dataframe of some actual sampled data, ensure that
    the get_pct_tracking_enabled outputs the correct dataframe
    :param addons_expanded: pytest fixture defined above
    :return: assertion whether the expected output indeed matches the true output
    """
    output = df_to_json(get_engagement_metrics(addons_expanded_day, main_summary_day))
    expected_output = [
        {
            "active_hours": 0.18194444444444444,
            "addon_id": u"baidu-code-update@mozillaonline.com",
            "avg_time_total": 747.0,
            "disabled": None,
        },
        {
            "active_hours": 0.18194444444444444,
            "addon_id": u"screenshots@mozilla.org",
            "avg_time_total": 747.0,
            "disabled": None,
        },
        {
            "active_hours": 0.18194444444444444,
            "addon_id": u"non-system-addon1",
            "avg_time_total": 747.0,
            "disabled": None,
        },
        {
            "active_hours": 0.18194444444444444,
            "addon_id": u"hotfix-update-xpi-intermediate@mozilla.com",
            "avg_time_total": 747.0,
            "disabled": None,
        },
        {
            "active_hours": 0.18194444444444444,
            "addon_id": u"fxmonitor@mozilla.org",
            "avg_time_total": 747.0,
            "disabled": None,
        },
        {
            "active_hours": 0.18194444444444444,
            "addon_id": u"non-system-addon2",
            "avg_time_total": 747.0,
            "disabled": None,
        },
        {
            "active_hours": 0.18194444444444444,
            "addon_id": u"formautofill@mozilla.org",
            "avg_time_total": 747.0,
            "disabled": None,
        },
        {
            "active_hours": 0.18194444444444444,
            "addon_id": u"webcompat@mozilla.org",
            "avg_time_total": 747.0,
            "disabled": None,
        },
    ]
    assert output == expected_output


def test_install_flows(events):
    output = df_to_json(install_flow_events(events))
    print("OUT", output)
    expected_output = [
        {
            "addon_id": "screenshots@mozilla.org",
            "installs": {"amo": 2, "unknown": 0},
            "download_times": {"amo": 584.5, "unknown": 0.0},
            "uninstalls": {"system-addon": 1},
        },
        {
            "addon_id": "fxmonitor@mozilla.org",
            "installs": None,
            "download_times": None,
            "uninstalls": {"system-addon": 1},
        },
        {
            "addon_id": "jid1-h4Ke2h5q31uuK7@jetpack",
            "installs": {"amo": 1, "unknown": 0},
            "download_times": {"amo": 1704.0, "unknown": 0.0},
            "uninstalls": None,
        },
        {
            "addon_id": "{87e997f4-ae0e-42e6-a780-ff73977188c5}",
            "installs": {"amo": 1, "unknown": 0},
            "download_times": {"amo": 3015.0, "unknown": 0.0},
            "uninstalls": None,
        },
        {
            "addon_id": "{08cc31c0-b1cb-461c-8ba2-95edd9e76a02}",
            "installs": {"amo": 1, "unknown": 0},
            "download_times": {"amo": 998.0, "unknown": 0.0},
            "uninstalls": None,
        },
        {
            "addon_id": "Directions_Found_mVBuOLkFzz@www.directionsfoundnt.com",
            "installs": {"amo": 0, "unknown": 1},
            "download_times": {"amo": 0.0, "unknown": 572.0},
            "uninstalls": None,
        },
    ]
    assert output == expected_output


def test_searches_and_ads(search_clients_daily, addons_expanded_day, spark):
    output = df_to_json(get_search_metrics(search_clients_daily, addons_expanded_day))
    print("OUT", output)
    expected_output = [
        {
            "addon_id": "baidu-code-update@mozillaonline.com",
            "sap_searches": {},
            "tagged_sap_searches": {"google": 10.0},
            "organic_searches": {},
            "search_with_ads": {"google": 3.0},
            "ad_click": {},
        },
        {
            "addon_id": "screenshots@mozilla.org",
            "sap_searches": {},
            "tagged_sap_searches": {"google": 10.0},
            "organic_searches": {},
            "search_with_ads": {"google": 3.0},
            "ad_click": {},
        },
        {
            "addon_id": "non-system-addon1",
            "sap_searches": {},
            "tagged_sap_searches": {"google": 10.0},
            "organic_searches": {},
            "search_with_ads": {"google": 3.0},
            "ad_click": {},
        },
        {
            "addon_id": "hotfix-update-xpi-intermediate@mozilla.com",
            "sap_searches": {},
            "tagged_sap_searches": {"google": 10.0},
            "organic_searches": {},
            "search_with_ads": {"google": 3.0},
            "ad_click": {},
        },
        {
            "addon_id": "fxmonitor@mozilla.org",
            "sap_searches": {},
            "tagged_sap_searches": {"google": 10.0},
            "organic_searches": {},
            "search_with_ads": {"google": 3.0},
            "ad_click": {},
        },
        {
            "addon_id": "non-system-addon2",
            "sap_searches": {},
            "tagged_sap_searches": {"google": 10.0},
            "organic_searches": {},
            "search_with_ads": {"google": 3.0},
            "ad_click": {},
        },
        {
            "addon_id": "formautofill@mozilla.org",
            "sap_searches": {},
            "tagged_sap_searches": {"google": 10.0},
            "organic_searches": {},
            "search_with_ads": {"google": 3.0},
            "ad_click": {},
        },
        {
            "addon_id": "webcompat@mozilla.org",
            "sap_searches": {},
            "tagged_sap_searches": {"google": 10.0},
            "organic_searches": {},
            "search_with_ads": {"google": 3.0},
            "ad_click": {},
        },
    ]

    assert output == expected_output
