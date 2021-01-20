import random
from selenium.webdriver.common.by import By
from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from util.conf import JIRA_SETTINGS


class WorkflowIssueLocators:
    field_issuetype = (By.ID, "type-val")
    input_issuetype = (By.ID, 'issuetype-field')
    issuetype_suggestions = (By.ID, 'issuetype-suggestions')
    issuetype_options = (By.CLASS_NAME, "aui-list-item")
    issuetype_submit = (By.CLASS_NAME, 'submit')
    btn_edit = (By.ID, "yest-btn-open-workflow-editor")
    palette_btn_task = (By.ID, "yest-workflow-editor-palette-task")
    palette_btn_start = (By.ID, "yest-workflow-editor-palette-start")
    btn_close = (By.ID, 'yest-btn-close-workflow-editor')
    btn_save_close = (By.ID, "yest-btn-save-close")
    message_wrong_permissions = (By.ID, "yest-warning-insufficient-rights")


def is_yest_workflow_type(element):
    return "yest-workflow" in element.get_attribute("class").lower()


def set_yest_workflow_issue_type(issue_page):
    field = issue_page.wait_until_clickable(WorkflowIssueLocators.field_issuetype)
    if field.text == 'Yest Workflow':
        return True
    else:
        field.click()
        issue_page.wait_until_clickable(WorkflowIssueLocators.input_issuetype).click()
        issue_page.wait_until_visible(WorkflowIssueLocators.issuetype_suggestions)
        issue_types = issue_page.get_elements(WorkflowIssueLocators.issuetype_options)

        filtered_issue_elements = list(filter(is_yest_workflow_type, issue_types))
        if filtered_issue_elements:
            rnd_issue_type_el = random.choice(filtered_issue_elements)
            issue_page.action_chains().move_to_element(rnd_issue_type_el).click(rnd_issue_type_el).perform()
            issue_page.wait_until_clickable(WorkflowIssueLocators.issuetype_submit).click()
            issue_page.wait_until_visible(WorkflowIssueLocators.btn_edit)
            return True
        else:
            return False


def app_yest4jira_edit(webdriver, datasets):
    page = BasePage(webdriver)
    app_specific_issue = random.choice(datasets['custom_issues'])
    issue_key = app_specific_issue[0]

    page.go_to_url(f"{JIRA_SETTINGS.server_url}/browse/{issue_key}")

    @print_timing("selenium_yest4jira:edit_workflow")
    def edit_workflow():
        page.wait_until_clickable(WorkflowIssueLocators.btn_edit).click()
        page.wait_until_visible(WorkflowIssueLocators.palette_btn_task).click()  # Wait for palette/task button
        page.get_element(WorkflowIssueLocators.palette_btn_start).click()  # exit editing mode (bof, bof...)
        page.get_element(WorkflowIssueLocators.btn_close).click()  # close
        page.wait_until_clickable(WorkflowIssueLocators.btn_save_close).click()  # Wait for 'save and close' button
        page.wait_until_invisible(WorkflowIssueLocators.btn_close)  # Wait for close button disappears
        page.wait_until_visible(WorkflowIssueLocators.btn_edit)  # Wait for edit button

    edit_button = page.wait_until_visible(WorkflowIssueLocators.btn_edit)
    if edit_button.is_enabled():
        edit_workflow()
    else:
        page.wait_until_visible(WorkflowIssueLocators.message_wrong_permissions)
