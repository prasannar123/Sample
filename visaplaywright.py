import asyncio
from undetected_playwright.sync_api import sync_playwright, Playwright
import argparse
import time

# Global variable
global exit_flag
exit_flag = False

# Create a parser object
parser = argparse.ArgumentParser(description='Script to automate web tasks.')

# Add command-line options
parser.add_argument('-m', '--month', type=int, default=16, help='Number of Months to select (1-100).')
parser.add_argument('-c', '--choices', type=str,
                    default="CHENNAI VAC,HYDERABAD VAC,KOLKATA VAC,MUMBAI VAC,NEW DELHI VAC",
                    help='List of choices, use comma separated')
parser.add_argument('-s', '--slotcount', type=int, default=5, help='slot count')

# Parse the command-line arguments
args = parser.parse_args()

# Access the value of the month option
selected_month = args.month
slotcount = args.slotcount

# Split the choices string and store it in a list
choices = [""] + args.choices.split(',') if args.choices else [args.choices]

def run(playwright: Playwright) -> None:
    args = []
    exit_flag = False
    # disable navigator.webdriver:true flag
    args.append("--disable-blink-features=AutomationControlled")
    browser = playwright.chromium.launch(headless=False, args=args)
    context = browser.new_context()
    page = context.new_page()
    # Set the viewport size
    #page.set_viewport_size({"width": 1820, "height": 1080})

    page.goto("https://www.usvisascheduling.com/en-US/")

    try:
        page.click("#continue_application", timeout=120000)  # Increase timeout to 60 seconds (60000 milliseconds)
    except playwright._impl._errors.TimeoutError as e:
        print("Timeout waiting for #continue_application:", e)

    print(page.title())  # Schedule Appointment

    page.wait_for_selector("#post_select", timeout=120000)
    ofc_post_element = page.get_by_label("OFC Post")
    ofc_post_text = ofc_post_element.text_content()

    list_of_options = [line.strip() for line in ofc_post_text.split('\n') if line.strip()]

    print(list_of_options)
    print(choices)
    page.wait_for_selector("#gm_select", timeout=120000)
    while True:
        time.sleep(1)
        try:
            for each_item in choices[1:]:
                print(each_item)
                if each_item in list_of_options:
                    if not exit_flag:
                        page.select_option("#post_select", '')
                        if exit_flag:
                            print("Selected slot.........")
                            time.sleep(6000)
                            break
                        else:
                            page.click("#post_select")

                            page.wait_for_selector("#post_select", timeout=120000)
                            page.select_option("#post_select", each_item)
                            # Wait for datepicker
                            #page.get_by_label("Date").is_visible(timeout=120000)

                            datepicker = None
                            start_time = time.time()
                            while time.time() - start_time < 120:  # Timeout after 120 seconds
                                print("waiting for .form-control.hasDatepicker")
                                datepicker = page.query_selector(".form-control.hasDatepicker")
                                if datepicker:
                                    break
                                time.sleep(1)
                            if not datepicker:
                                print("Timeout waiting for datepicker")
                                continue
                            datepicker.dblclick()
                            #datepicker.click()

                            if datepicker!=None:
                             for each in range(selected_month + 1):
                                if page.query_selector_all("td[class*='greenday']"):
                                    list_of_greendays = page.query_selector_all("td[class*='greenday']")
                                    print("number of green day available:", len(list_of_greendays))
                                    if len(list_of_greendays) == 1:
                                        datepicker = page.query_selector(".form-control.hasDatepicker")
                                        datepicker.click()
                                        page.wait_for_selector(".ui-icon.ui-icon-circle-triangle-e", timeout=120000)
                                        page.click(".ui-icon.ui-icon-circle-triangle-e")
                                    elif len(list_of_greendays) >= 2:
                                        for green_date in list_of_greendays[2:]:
                                            print(green_date)
                                            green_date.click()
                                            #time.sleep(10)



                                            page.wait_for_selector('.col-sm-6 label input', timeout=10000)
                                            list_of_availablity_slots = page.query_selector_all('.col-sm-6 label input')

                                            if list_of_availablity_slots == []:
                                                list_of_availablity_slots = page.query_selector('.col-sm-6 label input')
                                                if list_of_availablity_slots:
                                                     print("only one slot is available selecting next date....")
                                                     page.wait_for_selector("#datepicker", timeout=120000)
                                                     datepicker =  page.query_selector(
                                                         ".form-control.hasDatepicker")
                                                     datepicker.click()
                                                else:
                                                     print("Not found slots selecting next date......")
                                                     page.wait_for_selector("#datepicker", timeout=120000)
                                                     datepicker =  page.query_selector(
                                                         ".form-control.hasDatepicker")
                                                     datepicker.click()

                                            else:
                                                print("Radio button count:", len(list_of_availablity_slots))
                                                if len(list_of_availablity_slots) > 1:
                                                    for each_radio_button in list_of_availablity_slots:
                                                        data_slots =  each_radio_button.get_attribute('data-slots')
                                                        try:
                                                            slots = int(data_slots.strip())
                                                            print("Slots:", slots)
                                                            if slots >= slotcount:
                                                                each_radio_button.click()
                                                                exit_flag = True
                                                                break
                                                            else:
                                                                each_radio_button.click()
                                                                print("Selected slot...")
                                                                time.sleep(6000)
                                                                exit_flag = True
                                                                break
                                                        except (ValueError, AttributeError):
                                                            print(
                                                                "Error: Unable to convert data-slots to integer or data-slots attribute not found")
                                                            continue


                                                else:
                                                    print("no slots found", len(list_of_availablity_slots))
                                                    datepicker = page.query_selector(".form-control.hasDatepicker")
                                                    datepicker.click()
                                else:
                                    try:
                                        page.wait_for_selector(".ui-icon.ui-icon-circle-triangle-e", timeout=120000)
                                        page.click(".ui-icon.ui-icon-circle-triangle-e")
                                    except Exception as e:
                                        print("Exception:", e)
                                        continue
        except Exception as e:
            print("Exception:", e)
            continue

def main():
    with sync_playwright() as playwright:
        run(playwright)

main()
