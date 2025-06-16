
import streamlit as st
import xml.etree.ElementTree as ET
import time
import plotly.express as px
import pandas as pd
import math
import pandasql as ps


# ======== Upload button to trigger the application ========

st.write("# Upload XML:")

object_from_upload = st.file_uploader("")

if object_from_upload is None:
    st.info("When a file uploaded, application will start")
        

if object_from_upload is not None:
    st.success("Upload complete")

    # Data import 
    tree_element_data = ET.parse(object_from_upload)

    root = tree_element_data.getroot()
    print(f"root identified as {root}")

    # Data parsing from header
    value_customer = root[0][0].text
    value_invoice_num = root[0][1].text
    value_date = root[0][2].text

    currency = []
    for header_currency in root.findall('header'):
        get_currency = header_currency.find('price/currency').text
        currency.append(get_currency)
    
    currency = currency[0]


    value_total_sum = []
    for header_total_sum in root.findall('header'):
        total_sum = header_total_sum.find('price/total_sum').text
        value_total_sum.append(total_sum)

    # - necessary to change type to float
    value_total_sum = value_total_sum[0]
    value_total_sum = float(value_total_sum)

    value_total_sum_services = []
    for header_total_sum_services in root.findall('header'):
        total_sum_services = header_total_sum_services.find('price/total_sum_services').text
        value_total_sum_services.append(total_sum_services)
        

    # - necessary to change type to float
    value_total_sum_services = value_total_sum_services[0]
    value_total_sum_services_fl = float(value_total_sum_services)
    
 
    #  ----- DATA PARSING FROM DETAIL LEVEL XML ------
    value_category_list = []
    for detail_category in root.findall('detail'):
        category = detail_category.find('category').text
        value_category_list.append(category)


    value_product_name_list = []
    for detail_product_name in root.findall('detail'):
        product_name = detail_product_name.find('product_name').text
        value_product_name_list.append(product_name)


    value_price_list = []
    for detail_price in root.findall('detail'):
        product_price = detail_price.find('price_amount').text
        value_price_list.append(product_price)
    
    # change of type from string to float
    value_price_list_fl = list(map(float, value_price_list))


    
    value_attribut = []
    for detail_id in root.findall('detail'):
        ids = detail_id.get('id')
        value_attribut.append(ids)

    value_attribute_int = list(map(int, value_attribut))
    max_value_attribut = max(value_attribute_int)
    

    # Logic for recognizing whether any extra money for 'extended warranty' or 'insurance' 
    warranty = []
    for service_type in root.findall('detail'):
        condition_service_type = service_type.find('additional_service/service_type').text

        if condition_service_type == 'extended warranty':
            service_price = service_type.find('additional_service/service_price').text
            warranty.append(service_price)
        
    warranty_float = list(map(float, warranty)) 
    sum_price_warranty = math.fsum(warranty_float)
    

    insurance = []
    for service_type in root.findall('detail'):
        condition_service_type = service_type.find('additional_service/service_type').text

        if condition_service_type == 'insurance':
            service_price = service_type.find('additional_service/service_price').text
            insurance.append(service_price)
        
    insurance_float = list(map(float, insurance)) 
    sum_price_insurance = math.fsum(insurance_float)

    #Extra parsing for charts
    # Type of additional service <additional_service> - Including 'None'
    add_service_full = []
    for add_ser_item in root.findall('detail'):
        add_service = add_ser_item.find('additional_service/service_type').text
        add_service = add_service.capitalize()
        add_service_full.append(add_service)

    # Prices full - including '0.00' for None values
    add_ser_price_full = []
    for add_ser_price_item in root.findall('detail'):
        add_ser_price = add_ser_price_item.find('additional_service/service_price').text
        add_ser_price_full.append(add_ser_price)

    

    # Sum of prices - type change string -> float for calculation
    value_price_list_float = list(map(float, value_price_list)) 
    sum_price = math.fsum(value_price_list_float)
    
    # Data validation - total_sum = pri_values Y/N 
    value_total_sum_fl = float(value_total_sum)

    # Data type change for purpose of charts
    add_ser_price_full_float = list(map(float, add_ser_price_full)) 
    sum_adds_fl = math.fsum(add_ser_price_full_float)



    # v 3.2.X and higher - additional parsing for charts ---------------
    pro_price_where_insurance = []
    for price_amount in root.findall('detail'):
        condition_service_type = price_amount.find('additional_service/service_type').text

        if condition_service_type == 'insurance':
            price_amount = price_amount.find('price_amount').text
            pro_price_where_insurance.append(price_amount)
        
    pro_price_where_insurance = list(map(float, pro_price_where_insurance)) 
    sum_pro_price_where_insurance = math.fsum(pro_price_where_insurance)


    pro_price_where_ewarranty = []
    for price_amount in root.findall('detail'):
        condition_service_type = price_amount.find('additional_service/service_type').text

        if condition_service_type == 'extended warranty':
            price_amount = price_amount.find('price_amount').text
            pro_price_where_ewarranty.append(price_amount)
        
    pro_price_where_ewarranty = list(map(float, pro_price_where_ewarranty)) 
    sum_pro_price_where_ewarranty = math.fsum(pro_price_where_ewarranty)

    # --------------------------------------------------------------------



    # ======= Application Function for validation of detail line sum matches header values============

    # <total_sum>
    result_validation = []
    def data_validation(value_total_sum, sum_price):
        result = value_total_sum - sum_price
        st.write("---------")
        st.write("#### Validation process")
        ''
        st.write("1) ###### Validation process - Invoice sum = sum of items in lines:")
        
        if result < 0 or result > 0:
            st.warning("Validation not passed - summary does not equeal to line values. You can either continue with existing file or adjust the input file and upload it again.")
            st.write(f"** Total sum in the XML invoice is: '{value_total_sum:.2f}' but summary of prices in detail lines / per product is: '{sum_price:.2f}'.")
            outcome = ("Sum total - Not passed")
            result_validation.append(outcome)

        else:
            st.success("Validation passed")
            outcome = ("Sum total - Passed")
            result_validation.append(outcome)

    data_validation(value_total_sum_fl, sum_price)

    result_obj_outcome = result_validation[0]
   

    # Data validation - <total_sum_services> = value_total_sum_services Y/N 
    
    result_validation_services = []
    def data_validation_services(value_total_sum_services_fl, sum_price_warranty , sum_price_insurance):
        result = value_total_sum_services_fl - sum_price_warranty - sum_price_insurance
        sum_warranty_insurance = sum_price_warranty + sum_price_insurance
        st.write("2) ###### Validation process - Invoice sum services = sum of items in lines:")
        
        if result < 0 or result > 0:
            st.warning("Validation not passed - summary does not equeal to line values. You can either continue with existing file or adjust the input file and upload it again.")
            st.write(f"** Total sum of SERVICES in the XML invoice is: '{value_total_sum_services_fl:.2f}' but summary of prices in detail lines is '{sum_warranty_insurance:.2f}'.")
            outcome = ("Services - Not passed")
            result_validation_services.append(outcome)

        else:
            st.success("Validation passed")
            outcome = ("Services - Passed")
            result_validation_services.append(outcome)

    data_validation_services(value_total_sum_services_fl, sum_price_warranty , sum_price_insurance)

    result_obj_outcome_services = result_validation_services[0]


    ''
    ''
    with st.expander(
        "Help",
        icon= ":material/help_outline:"
	    ):

        ''
        st.write("""
        - If validation **not passed**, it is because summary of either 1. or 2. (or both) are not matching with values in detail
        - This is an alert that some of the values visualized in the dashbords bellow will **not be correct**
        - More details on the data parsing and validation here:
        """)

        ''
        # st.page_link(
        #     label = "XML princpiles for this application",
        #     page="Subpages/F1_F2_description_XML_XSD.py",
        #     help="The button will redirect to the relevant page within this app.",
        #     use_container_width=True,
        #     icon=":material/launch:",
        #     ) 
        ''
        ''
        # st.image("Pictures/Function_2/F2_validation_xml.png")


    # ========= Button to show values parsed and calculated ======================

    value_to_paid = value_total_sum + sum_price_warranty + sum_price_insurance

    st.write("------")
    st.write("#### Data Visualization:")
    ''
    ''
    with st.expander("Summary overview - Invoice", icon = ":material/apps:"):
        ''
        '' 
        st.write(f"**Sumary:**")
        st.write(f" - Invoice number: **{value_invoice_num}**")
        st.write(f" - Receiver of the invoice: **{value_customer}**")
        st.write(f" - Invoice from date (YYYY-MM-DD): **{value_date}**")

        st.write(f" - Price to be paid: **{value_to_paid:.2f} {currency}** (*products + services)")
        st.write(f" - Number of products: **{max_value_attribut}**")
        ''
        ''
        ''
        st.write(f"**Detail:**")
        st.write(f" - Total sum of products: **{value_total_sum:.2f} {currency}**")

        sum_additional_serv = sum_price_warranty + sum_price_insurance

        st.write(f" - Sum of additional services: **{sum_additional_serv:.2f} {currency}**")
        st.write(f" - Extended warranty: **{sum_price_warranty:.2f} {currency}**")
        st.write(f" - Insurance: **{sum_price_insurance:.2f} {currency}**")
        ''
        ''

    # Transformation of Data to table -> not editable
    data_table = pd.DataFrame({
        "Order" : value_attribut,
        "Product" : value_product_name_list,
        "Price" : value_price_list_fl, # must be float due to filtring in table    
        "Category" : value_category_list, 
        "Additional service" : add_service_full, 
        "Additional service price" : add_ser_price_full_float  # must be float due to filtring in table                
        })

    
    data_table_sql = pd.DataFrame({
        "Order" : value_attribut,
        "Product" : value_product_name_list,
        "Price" : value_price_list_fl, # must be float due to filtring in table    
        "Category" : value_category_list, 
        "Additional_service" : add_service_full, 
        "Additional_service_price" : add_ser_price_full_float  # must be float due to filtring in table                
        })



    with st.expander("SQL Queries 1 - Overview", icon = ":material/view_list:"):
        ''
        '' 

        # Number of items in each product category 
        q0a = """SELECT category, count(*) as 'count'
        FROM
            data_table_sql
        GROUP BY
            Category
        ORDER BY 
            count DESC
        """


        st.write("- Number of items in **each product Category**:")
        st.dataframe(ps.sqldf(q0a, locals()), hide_index=True, use_container_width=True)

        # Number of items with additional service
        q0b = """SELECT Additional_service, count(*) as 'count'
        FROM
            data_table_sql
        
        WHERE 
            Additional_service IS NOT 'None'
            
        GROUP BY
            Additional_service
        ORDER BY 
            count DESC
        """

        ''
        ''
        st.write("- Number of items having **additional services**:")
        st.dataframe(ps.sqldf(q0b, locals()), hide_index=True, use_container_width=True)

        # Number of items with  NO additional service = 'None'
        q0c = """SELECT Additional_service, count(*) as 'count'
        FROM
            data_table_sql
        
        WHERE 
            Additional_service = 'None'
            
        GROUP BY
            Additional_service
        ORDER BY 
            count DESC
        """

        ''
        ''
        st.write("- Number of items **without** any additional service")
        st.dataframe(ps.sqldf(q0c, locals()), hide_index=True, use_container_width=True)


    with st.expander("SQL Queries 2 - Prices/Costs", icon = ":material/view_list:"):
        ''
        ''
        st.write(f"- Currency: **{currency}**")
        ''
        '' 
        # The most expensive item
        q1 = """SELECT *
        FROM
            data_table_sql
        ORDER BY
            Price DESC
        LIMIT 1"""

        st.write("- The **most expensive** item (Price):")
        st.dataframe(ps.sqldf(q1, locals()), hide_index=True, use_container_width=True)


        # The most expensive item including Additional service
        q2 = """SELECT *
        FROM
            data_table_sql
        WHERE
            Additional_service = 'Extended warranty'
        ORDER BY
            Additional_service_price DESC
        LIMIT 1"""

        q2b = """SELECT *
        FROM
            data_table_sql
        WHERE
            Additional_service = 'Insurance'
        ORDER BY
            Additional_service_price DESC
        LIMIT 1"""


        ''
        ''
        st.write("- The **most expensive additional service** (Extended warranty and Insurance):")
        st.dataframe(ps.sqldf(q2, locals()), hide_index=True, use_container_width=True)
        st.dataframe(ps.sqldf(q2b, locals()), hide_index=True, use_container_width=True)

        # The cheapest item
        q3 = """SELECT *
        FROM
            data_table_sql
        ORDER BY
            (Price + 'Additional service price') ASC
        LIMIT 1"""


        ''
        ''
        st.write("- The **cheapest** item (lowest Price):")
        st.dataframe(ps.sqldf(q3, locals()), hide_index=True, use_container_width=True)


        # The cheapest additional services
        q4 = """SELECT *
        FROM
            data_table_sql
        WHERE
            Additional_service = 'Extended warranty'
        ORDER BY
            Additional_service_price ASC
        LIMIT 1"""

        q4b = """SELECT *
        FROM
            data_table_sql
        WHERE
            Additional_service = 'Insurance'
        ORDER BY
            Additional_service_price ASC
        LIMIT 1"""


        ''
        ''
        st.write("- The **cheapest additional service** (Extended warranty and Insurance):")
        st.dataframe(ps.sqldf(q4, locals()), hide_index=True, use_container_width=True)
        st.dataframe(ps.sqldf(q4b, locals()), hide_index=True, use_container_width=True)
    
    # ========= Data Visualization ====================
    ''
    ''
    ''
    ''
    st.write("##### Interactive table and charts:")

    unique_value = data_table['Category'].unique()

    # Multiselect filter
    ''
    filter_multiselect = st.multiselect(
        "Select category",
        unique_value,
        default = unique_value,
        help = "Select category which you want to see. Multiple categories allowed"
    )  
    
    if not len(filter_multiselect):
        st.warning("Select at lease 1 category to see overview table and charts")

    # min_value_price = data_table['Price'].min()
    # max_value_price = data_table['Price'].max()
    
    
    # Slider na price, zatím nefunkcni
    # from_price, to_price = st.slider(
    #     "Filter Price",
    #     min_value = min_value_price,
    #     max_value = max_value_price,
    #     help = "Select range of prices you want to see"
    # )
    
    
    filtered_data = data_table[
    (data_table["Category"].isin(filter_multiselect))
    # & (data_table["Price"] <= max_value_price)
    # & (min_value_price <= data_table["Price"]) 
    ]

    # This is adjusting the table
    ''
    data_table_2 = st.dataframe(data=filtered_data, hide_index=True, use_container_width=True)

    

    # Pie chart
    data = pd.DataFrame({
        "Product" : value_product_name_list,
        "Price" : value_price_list
        })


    fig_pie = px.pie(
        filtered_data, 
        names = "Product",
        values = "Price",
        title = "Costs - ratio of product prices"
        )

    with st.container(border=True):
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Bar chart
    fig_bar = px.bar(
        filtered_data, 
        x="Product",
        y="Price",
        title= "Bar chart - Costs - ratio of product prices",
        )

    with st.container(border=True):
        st.plotly_chart(fig_bar, use_container_width=True)


    # 15-June - testuju
    # Bar chart 2 -  Price + Additional service price
    # It is important to have values in float!!! to be able to 'sum' them as part of visualizing in the chart
    data_bar_2 = ({
        "Product" : value_product_name_list,
        "Price" : value_price_list_float,  #float is must 
        "Category" : value_category_list, 
        "Additional service" : add_service_full, 
        "Additional service price" : add_ser_price_full_float #float is must 
    })

    ''
    ''
    ''
    st.write("##### Static Charts:")

    fig_bar_2 = px.bar(data_bar_2,
            x="Product",
            y=["Price","Additional service price"],
            title="Bar chart - Ratio of price including extra costs for additional services",
            )

    with st.container(border=True):
        st.plotly_chart(fig_bar_2, use_container_width=True)


    # v4.0 - new charts ---------------------------------------

    data_pie_2 = pd.DataFrame({

    "Costs" : [value_total_sum_fl,sum_adds_fl],
    "Costs name" : ["Sum price","Sum additional services"],

    })


    fig_pie_2 = px.pie(
        data_pie_2, 
        names = "Costs name",
        values = "Costs",
        title = "How much additional services increase the costs"
        )

    with st.container(border=True):
        st.plotly_chart(fig_pie_2, use_container_width=True)
        st.write(f"- Costs for products **{value_total_sum_fl:.2f}** {currency}")
        st.write(f"- Costs for additional services **{sum_adds_fl:.2f}** {currency}")
        st.write(f"- Summary:  **{(sum_adds_fl + value_total_sum_fl):.2f}** {currency}")



    col1, col2 = st.columns(2)

    data_pie_3 = pd.DataFrame({

    "Costs" : [sum_pro_price_where_insurance,sum_price_insurance],
    "Costs named" : ["Costs products","Costs Insurance"],

    })

    fig_pie_3 = px.pie(
        data_pie_3, 
        names = "Costs named",
        values = "Costs",
        title = "Costs Insurance"
        )
    



    data_pie_4 = pd.DataFrame({

    "Costs" : [sum_pro_price_where_ewarranty,sum_price_warranty],
    "Costs names" : ["Costs products","Costs warranty"],

    })

    fig_pie_4 = px.pie(
        data_pie_4, 
        names = "Costs names",
        values = "Costs",
        title = "Costs Extended warranty"
        )  



    with col1.container(border=True):
            st.write(fig_pie_3)
            st.write(f"- Product costs: **{sum_pro_price_where_insurance:.2f}** {currency}")
            st.write(f"- The insurance: **{sum_price_insurance:.2f}** {currency}")
            st.write(f"- Summary:  **{(sum_pro_price_where_insurance + sum_price_insurance):.2f}** {currency}")



    with col2.container(border=True):
        st.write(fig_pie_4)
        st.write(f"- Product costs: **{sum_pro_price_where_ewarranty:.2f}** {currency}")
        st.write(f"- The warranty: **{sum_price_warranty:.2f}** {currency}")
        st.write(f"- Summary:  **{(sum_pro_price_where_ewarranty + sum_price_warranty):.2f}** {currency}")
    
    #----------------------------------------------------------------------------

    # Final outcome for print - using SERVER time
    st.write("------")
    st.write("#### Download of .txt:")
    st.write('''A short summary of the original XML invoice, including result of validation, date and some of the parsed data.''')

    st.image("Pictures/V2_pictures/txt outcome_3.png")


    # Time 
    time_objects = time.localtime()
    year, month, day, hour, minute, second, weekday, yearday, daylight = time_objects  

    date_custom = str("Date: %02d-%02d-%04d" % (day,month,year))
    time_custom = str("Time: %02d:%02d:%02d" % (hour,minute,second))
    day_custom = str(("Mon","Tue","Wed","Thu","Fri","Sat","Sun") [weekday])
    day_custom_2 = str("Day: "+ day_custom)
    full_date_outcome = str(date_custom +" | " + day_custom_2 +" | " + time_custom )

    final_outcome = (f"{full_date_outcome} | Validation: 1. {result_obj_outcome}, 2. {result_obj_outcome_services} | Receiver: {value_customer} | Price to pay (including extra services): {value_to_paid:.2f} {currency}.")


    file_name_fstring = f"Summary-{value_invoice_num}.txt"

    ''
    ''
    ''
    if st.download_button(
        "Download",
        data= final_outcome,
        file_name= file_name_fstring,
        icon = ":material/download:",
        use_container_width=True):
            
        st.info("download will start in few seconds")

st.write("-------")
