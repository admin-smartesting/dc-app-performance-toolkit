import random
from selenium.webdriver.common.by import By
from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from util.conf import JIRA_SETTINGS


class ImportLocators:
    menu_import = (By.ID, "yest-btn-main-import")
    tile_sample = (By.ID, "yest-tile-import-sample")
    select_project = (By.ID, "yest-import-select-project")
    select_options = (By.CLASS_NAME, "react-select__option")
    btn_import = (By.ID, 'yest-btn-import-doImport')
    btn_terminate = (By.ID, 'yest-btn-import-sample-terminate')
    tile_sample_LR = (By.ID, 'yest-tile-sample-LR')
    error_message = (By.ID, "yest-error-no-attachment-creation-right")


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


def is_import(btn):
    @print_timing("selenium_yest4jira_import:is_import")
    def measure():
        return "doImport" in btn.get_attribute("data-testid")

    return measure();


def import_sample(page, sample_tile_locator):
    page.wait_until_clickable(ImportLocators.tile_sample).click()
    page.wait_until_clickable(sample_tile_locator).click()  # Click sample
    page.wait_until_clickable(ImportLocators.select_project).click()
    yest_projects = page.get_elements(ImportLocators.select_options)
    if yest_projects:
        rnd_project_el = random.choice(yest_projects)
        page.action_chains().move_to_element(rnd_project_el).click(rnd_project_el).perform()
        page.wait_until_clickable(ImportLocators.btn_import)  # Wait button 'import'
        btn_import = page.get_element(ImportLocators.btn_import)
        if is_import(btn_import):
            btn_import.click()
            page.wait_until_clickable(ImportLocators.btn_terminate).click()  # Click button 'Terminate'
            page.wait_until_visible(ImportLocators.tile_sample)  # Wait for Yest Sample tile
        else:
            page.wait_until_visible(ImportLocators.error_message)
            btn_import.click()
            page.wait_until_visible(ImportLocators.tile_sample)  # Wait for Yest Sample tile


def app_yest4jira_import(webdriver, datasets):
    page = BasePage(webdriver)

    @print_timing("selenium_yest4jira_import")
    def measure():
        page.go_to_url(f"{JIRA_SETTINGS.server_url}/plugins/servlet/yest/mainPage")
        page.wait_until_clickable(ImportLocators.menu_import).click()  # Wait for import button
        import_sample(page, ImportLocators.tile_sample_LR)  # import sample Leave Request

    measure()


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

    installed = set_yest_workflow_issue_type(page)
    if installed:
        edit_button = page.wait_until_visible(WorkflowIssueLocators.btn_edit)
        if edit_button.is_enabled():
            edit_workflow()
        else:
            page.wait_until_visible(WorkflowIssueLocators.message_wrong_permissions)
