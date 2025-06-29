from bs4 import BeautifulSoup

# List of components
components = ["component1", "component2", "component3"]

# Create a list to store the locators
locators = []

for component in components:
    # Open the local HTML file
    with open(f"{component}.html", "r") as f:
        html = f.read()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Find all input elements within the component
    input_elements = soup.find_all('input')
    for input_element in input_elements:
        locator = input_element.get('id')
        if locator:
            locators.append(f"by.id('{locator}')")
        else:
            locator = input_element.get('name')
            if locator:
                locators.append(f"by.name('{locator}')")
            else:
                locator = input_element.get('class')
                if locator:
                    locators.append(f"by.css_selector('.{locator}')")
                else:
                    locator = input_element.get('xpath')
                    locators.append(f"by.xpath('{locator}')")

    # Find all button elements within the component
    button_elements = soup.find_all('button')
    for button_element in button_elements:
        locator = button_element.get('id')
        if locator:
            locators.append(f"by.id('{locator}')")
        else:
            locator = button_element.get('name')
            if locator:
                locators.append(f"by.name('{locator}')")
            else:
                locator = button_element.get('class')
                if locator:
                    locators.append(f"by.css_selector('.{locator}')")
                else:
                    locator = button_element.get('xpath')
                    locators.append(f"by.xpath('{locator}')")

# Write the locators to a text file
with open("locators.txt", "w") as f:
    for locator in locators:
        f.write(locator + "\n")