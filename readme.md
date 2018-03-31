
This test script has been created for two products "Multi Reverse Convertible" and  "Multi Barrier Reverse Convertible". The URLs of the pricing form for both the products have been hardcoded. The API takes in the input values from the user, injects into the pricing forms and displays the final result of both the products.

Installation :

1) Copy the folder and extract its contents. This will create a deritrade folder.
2) Create a virtual environment with the following command (Linux system):
	 
	virtualenv venv

3) Activate the virtual environemnt:

	source venv/bin/activate

4) Now install all the dependencies present in requirements.txt.

	pip install -r requirements.txt

5) Now migrate the django models.

	python manage.py migrate


Running the code:


1) Run the server with the following command:

	python manage.py runserver

2) Hit the following URL in the browser. This is the API for the pricing form.

	http://127.0.0.1:8000/pricingform/

3) Now the input object can be posted under the Raw data tab, within the content field. A sample input object is as follows:
   
	{
    "Domicile": ["Switzerland","Switzerland"],
    "Settlement": ["Cash","Cash"],
    "Currency": ["USD","EUR"],
    "Amount": ["100000", "50k"],
    "InitialFixing": ["<today's date(dd/mm/yyyy)","<today's date(dd/mm/yyyy)>"],
    "FinalFixing": ["01/11/2019", "1y"],
    "TimeType": ["Now", "Now"],
    "SolveFor": ["Coupon","Coupon"],
    "Strike": ["100","100"],
    "Coupon": [],
    "Barrier": ["0","70"],
    "Frequency": ["Quarterly","Monthly"],
    "Commission": ["0","2"],
    "CreditType": ["Sales credit","Sales credit"],
    "Listing": ["Not listed","Not listed"],
    "UnderLying": {"productType=41" : ["Apple","IBM"], "productType=12" : ["Apple","IBM", "FCA"]}
	}

4) After hitting POST, a new firefox browser session opens up and injects the input object values into both the pricing forms one by one. It then fetches the result and and API returns a JSON output.

	


