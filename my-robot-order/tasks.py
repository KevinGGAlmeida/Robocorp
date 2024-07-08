from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import os
from pathlib import Path


@task
def order_robots_from_RobotSpareBin():
    """
    Order robots from RobotSpare
    """
    open_the_intranet_website()
    download_orders()
    fullfilling_form()
    create_zipfile()


def download_orders():
    """
    Download orders data file
    """
    HTTP().download(
        url="https://robotsparebinindustries.com/orders.csv", overwrite=True
    )


def fullfilling_form():
    """
    Fullfilling the form and downloading exporting to pdf
    """
    data = Tables().read_table_from_csv("orders.csv")
    for row in data:
        if fill_form(row) == "Request error":
            continue
        export_as_pdf(row["Order number"])
        order_another_robot()


def open_the_intranet_website():
    """
    Navigate to given URL
    """
    browser.goto("https://robotsparebinindustries.com/#/robot-order")


def fill_form(data):
    """
    Filling out form
    """
    page = browser.page()
    page.click("text=OK")
    page.select_option("#head", data["Head"])
    page.click(f"#id-body-{data['Body']}")
    page.fill(
        '//input[@placeholder="Enter the part number for the legs"]', data["Legs"]
    )
    page.fill("#address", data["Address"])
    page.click("#order")
    if page.locator('//*[@class="alert alert-danger"]').is_visible() == True:
        page.reload()
        return "Request error"


def export_as_pdf(order_num):
    """
    Export the data to a pdf file
    """
    page = browser.page()
    page.wait_for_timeout(2000)
    receipt_result = page.locator("#order-completion").inner_html()
    page.locator("#robot-preview-image").screenshot(
        path=f"{Path.cwd()}/output/result/res.png"
    )
    pdf = PDF()
    pdf.html_to_pdf(
        [receipt_result], f"{Path.cwd()}/output/result/receipt{order_num}.pdf"
    )
    pdf.add_files_to_pdf(
        [
            f"{Path.cwd()}/output/result/receipt{order_num}.pdf",
            f"{Path.cwd()}/output/result/res.png",
        ],
        target_document=f"{Path.cwd()}/output/result/receipt{order_num}.pdf",
    )
    os.remove(f"{Path.cwd()}/output/result/res.png")


def order_another_robot():
    """
    Click on ORDER ANOTHER ROBOT
    """
    browser.page().click("text=ORDER ANOTHER ROBOT")


def create_zipfile():
    """
    Creating another zipfile
    """
    Archive().archive_folder_with_zip(
        f"{Path.cwd()}/output/result", f"{Path.cwd()}/output/result.zip"
    )
