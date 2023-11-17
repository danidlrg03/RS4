from dash.testing.application_runners import import_app

def test_one(dash_br):
    app = import_app("/dash_test.app")
    dash_br.server_url = "Hosted URL"
    assert dash_br.wait_for_element_by_id("filedropdown")
    assert dash_br.wait_for_element_by_id("datatable_id")
    assert dash_br.wait_for_element_by_id("dropdown")
    assert dash_br.wait_for_element_by_id("chart")
    assert dash_br.wait_for_element_by_id("racetrack")
    return None
