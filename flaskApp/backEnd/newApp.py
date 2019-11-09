import pandas as pd
import operator
import matplotlib.pyplot as plt
import matplotlib.cm
from itertools import groupby
from IPython import get_ipython
from matplotlib.colors import Normalize
import numpy as np
import seaborn as sns
import math
import json


from flask import Flask, jsonify, request #import objects from the Flask model
from flask_cors import CORS
app = Flask(__name__) #define app using Flask
CORS(app)

@app.route('/', methods=['GET'])
def test():
	return jsonify({'message' : 'It works!'})

@app.route('/census/', methods=['GET'])
def returnSimilarity():
    main_diff = []
    param = {}
    df_s1 = pd.DataFrame()
    df_s2 = pd.DataFrame()
    param = request.args.to_dict()
    param["s1"]=param["s1"].upper()
    param["s2"]=param["s2"].upper()

    if param["s1"] == 'DELHI':
        param["s1"] = 'NCT OF DELHI'  

    if param["s2"] == 'DELHI':
        param["s2"] = 'NCT OF DELHI'    

    

    #code here for all similarity
    if len(param) == 2:
        # Load dataset
        data = pd.read_csv("india-districts-census-2011.csv")
        df_s1 = data.loc[data['State name'] == param["s1"]]
        df_s2 = data.loc[data['State name'] == param["s2"]]
        main_diff = allSimilarity(df_s1,df_s2,data)

    if len(param) >= 3:
        category = param["selectedCategory"]
        # Load dataset
        newData = pd.read_csv("india-districts-census-2011.csv")

        if category == "Caste":
            newData = newData[['District code', 'State name', 'District name', 'SC', 'Male_SC', 'Female_SC', 'ST', 'Male_ST', 'Female_ST']].copy()
        elif category == "Religion":
            newData = newData[['District code', 'State name', 'District name', 'Hindus', 'Muslims', 'Christians', 'Sikhs', 'Buddhists', 'Jains', 'Others_Religions', 'Religion_Not_Stated']].copy()
        elif category == "Workers":
            newData = newData[['District code', 'State name', 'District name', 'Workers', 'Male_Workers', 'Female_Workers', 'Main_Workers', 'Marginal_Workers', 'Non_Workers', 'Cultivator_Workers', 'Agricultural_Workers', 'Household_Workers', 'Other_Workers']].copy()
        elif category == "Education":
            newData = newData[['District code', 'State name', 'District name', 'Below_Primary_Education','Primary_Education','Middle_Education','Secondary_Education','Higher_Education','Graduate_Education','Other_Education','Literate_Education','Illiterate_Education','Total_Education','Male_Literate','Female_Literate']].copy()
        elif category == "Basic_needs":
            newData = newData[['District code', 'State name', 'District name', 'LPG_or_PNG_Households','Housholds_with_Electric_Lighting','Type_of_bathing_facility_Enclosure_without_roof_Households','Type_of_fuel_used_for_cooking_Any_other_Households','Type_of_latrine_facility_Pit_latrine_Households','Type_of_latrine_facility_Other_latrine_Households','Type_of_latrine_facility_Night_soil_disposed_into_open_drain_Households','Type_of_latrine_facility_Flush_pour_flush_latrine_connected_to_other_system_Households','Not_having_bathing_facility_within_the_premises_Total_Households','Not_having_latrine_facility_within_the_premises_Alternative_source_Open_Households','Main_source_of_drinking_water_Un_covered_well_Households','Main_source_of_drinking_water_Handpump_Tubewell_Borewell_Households','Main_source_of_drinking_water_Spring_Households','Main_source_of_drinking_water_River_Canal_Households','Main_source_of_drinking_water_Other_sources_Households','Main_source_of_drinking_water_Other_sources_Spring_River_Canal_Tank_Pond_Lake_Other_sources__Households','Location_of_drinking_water_source_Near_the_premises_Households','Location_of_drinking_water_source_Within_the_premises_Households','Main_source_of_drinking_water_Tank_Pond_Lake_Households','Main_source_of_drinking_water_Tapwater_Households','Main_source_of_drinking_water_Tubewell_Borehole','Location_of_drinking_water_source_Away_Households']].copy()
        elif category == "Living_standards":
            newData = newData[['District code', 'State name', 'District name', 'Households_with_separate_kitchen_Cooking_inside_house','Household_size_1_person_Households','Household_size_2_persons_Households','Household_size_1_to_2_persons','Household_size_3_persons_Households','Household_size_3_to_5_persons_Households','Household_size_4_persons_Households','Household_size_5_persons_Households','Household_size_6_8_persons_Households','Household_size_9_persons_and_above_Households']].copy()
        elif category == "Socio_economic_status":
            newData = newData[['District code', 'State name', 'District name', 'Households_with_Computer','Households_with_Bicycle','Households_with_Car_Jeep_Van','Households_with_Radio_Transistor','Households_with_Scooter_Motorcycle_Moped','Households_with_Telephone_Mobile_Phone_Landline_only','Households_with_Telephone_Mobile_Phone_Mobile_only','Households_with_TV_Computer_Laptop_Telephone_mobile_phone_and_Scooter_Car','Households_with_Television','Households_with_Telephone_Mobile_Phone','Households_with_Telephone_Mobile_Phone_Both']].copy()

        if len(param) == 4:
            subCategory = param["selectedSubCategory"]
            newData = newData[['District code', 'State name', 'District name', subCategory]].copy()

        df_s1 = newData.loc[newData['State name'] == param["s1"]]
        df_s2 = newData.loc[newData['State name'] == param["s2"]]

        main_diff = categorySimilarity(df_s1,df_s2,newData)


    max_val = 0
    max_index1 = 0
    max_index2 = 0
    for i in range(len(main_diff)):
        for j in range(len(main_diff[i])):
            if(main_diff[i][j] > max_val):
                max_val = main_diff[i][j]
                max_index1 = i
                max_index2 = j

    print(param)

    # Jsonify the returned matrix data
    state_one_districts = df_s1['District name'].values
    state_two_districts = df_s2['District name'].values
    row = len(state_one_districts)
    col = len(state_two_districts)
    jsonData = []

    norm=Normalize()
    main_diff = norm(main_diff)

    for i in range(0,row):
        state_one = state_one_districts[i]
        for j in range(0,col):
            state_two = state_two_districts[j]
            unit = {
                "State One": state_one,
                "State Two": state_two,
                "value": str(main_diff[i][j])   
            }
            jsonData.append(unit)

    print(state_one_districts)
    print(state_two_districts)
    print(jsonData)

    similarityValue = "%s from %s and %s from %s are most similar" %(df_s1['District name'].iloc[max_index1].upper(),param["s1"],df_s2['District name'].iloc[max_index2].upper(),param["s2"])

    responseData = {
        "Similarity" : similarityValue,
        "Data" : jsonData
    }

    return jsonify(responseData)

#code here for all similarity
def allSimilarity(df_s1,df_s2,data):
    df_s1.set_index('District code')
    df_s2.set_index('District code')
    main_diff = []
    
    for row1 in df_s1.iterrows():
        diff=[]
        for row2 in df_s2.iterrows():
            dist = 0
            for column in list(data)[3:]:
                max_col = max(data[column])
                min_col = min(data[column])
                dist += pow((row1[1][column] - row2[1][column])/(max_col - min_col),2)
            diff.append(1/math.sqrt(dist))
        main_diff.append(diff)

    return main_diff

#code inside categoryData
def categorySimilarity(df1, df2, data_Category):
    # Set indices for both the data frames
    df1.set_index('District code')
    df2.set_index('District code')
    
    # The similarity matrix of size len(df1) X len(df2)
    main_diff = []
    
    # Iterate through rows of df1
    for row1 in df1.iterrows(): 
        # Create list to hold similarity score of row1 with other rows of df2
        diff=[]
        # Iterate through rows of df2
        for row2 in df2.iterrows():
            # Calculate sum of squared differences
            dist = 0
            for column in list(data_Category)[3:]:
                max_col = max(data_Category[column])
                min_col = min(data_Category[column]) 
    
                dist += pow((row1[1][column] - row2[1][column])/(max_col - min_col),2)
            # Take sqrt and inverse the result
            diff.append(1/math.sqrt(dist))
        # Append similarity scores
        main_diff.append(diff)

    # Find the max value of similarity score from lists of lists
    max_val = 0
    max_index1 = 0
    max_index2 = 0
    for i in range(len(main_diff)):

        for j in range(len(main_diff[i])):
            if(main_diff[i][j] > max_val):
                max_val = main_diff[i][j]
                max_index1 = i
                max_index2 = j
                
    print ("\n%s and %s are most similar" %(df1['District name'].iloc[max_index1],df2['District name'].iloc[max_index2]))
    print ("Similarity Score: %s" %(max_val))
    print ("\nUnder parameters: \n")
    for col in data_Category.columns: 
        print(col) 
                
    return main_diff


if __name__ == '__main__':
	app.run(debug=True, port=8080) #run app on port 8080 in debug mode