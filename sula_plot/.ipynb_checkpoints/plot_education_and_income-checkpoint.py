import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from typing import Dict, List, Tuple


def extract_countries_and_values(
    file_name: str, 
    countries: str, 
    countries_list: list[str], 
    education_type: str, 
    education_values_list: list[str],
    column_values: str, 
    income: str,  
    period: str,  
    delimiter=',', 
    encoding='utf-8',
    chunk_size=10000 
) -> dict[str, list[tuple[str, float]]]: 
    result = {}

    try:
        for chunk in pd.read_csv(file_name, delimiter=delimiter, encoding=encoding, 
                                 usecols=[countries, education_type, column_values, income, 'Sex', period] if income else [countries, education_type, column_values, 'Sex', period],
                                 chunksize=chunk_size, on_bad_lines='skip'):
            period_data = [2020]
            sex = 'Sex'
            list_sex = ['Female']
            chunk = chunk[chunk[countries].isin(countries_list)]
            chunk = chunk[chunk[education_type].isin(education_values_list)]
            chunk = chunk[chunk[sex].isin(list_sex)]
            chunk = chunk[chunk[period].isin(period_data)]

            
            chunk = chunk.drop_duplicates(subset=[countries, education_type, column_values])

            
            if income:
                chunk = chunk.dropna(subset=[education_type, column_values, income])
            else:
                chunk = chunk.dropna(subset=[education_type, column_values])

            
            chunk[column_values] = pd.to_numeric(chunk[column_values], errors='coerce')

           
            if income:
                chunk = chunk[chunk[income].str.strip().str.lower() == 'above 100% of median income'.lower()]
            
            chunk = chunk.drop_duplicates(subset=[countries, education_type, column_values])
            chunk_result = (
                chunk.groupby([countries, education_type])  
                .agg({column_values: 'first'})  
                .reset_index()  
            )

            for _, row in chunk_result.iterrows():
                country = row[countries]
                education_values_list_value = row[education_type]
                value = row[column_values]  

                
                if country not in result:
                    result[country] = [(education_values_list_value, value)]  
                else:
                    
                    if not any(edu[0] == education_values_list_value for edu in result[country]):
                        result[country].append((education_values_list_value, value)) 
       

        return result  

    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
        return {}
    except pd.errors.ParserError as e:
        print(f"Parsing error: {e}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {}


def solve_data(
    result_education: dict[str, list[tuple[str, float]]],
    result_income: dict[str, list[tuple[str, float]]]):

    countries = list(result_education.keys())
    colors = ['r', 'g', 'b', 'm', 'c', 'y', 'orange']
    markers = ['o', 'D', 'v']
    education_levels_i = ['Below upper secondary education', 'Upper secondary education', 'Bachelor\'s, master\'s, doctoral or equivalent level']
    education_levels_e = ['Primary education', 'Upper secondary education', 'Bachelor\'s, Master\'s and Doctoral or equivalent level']
    country_colors = {countries[i]: colors[i] for i in range(len(countries))}

    legend_handles_education = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='darkgray', markersize=10, label='Primary education'),
        Line2D([0], [0], marker='D', color='w', markerfacecolor='darkgray', markersize=10, label='Upper secondary education'),
        Line2D([0], [0], marker='v', color='w', markerfacecolor='darkgray', markersize=10, label='Bachelors, Masters and Doctoral or equivalent level')
    ]
    

    plt.figure(figsize=(9, 6))
    plt.xlabel('Education Level percent population(%)', fontsize=10)
    plt.ylabel('Income Level (%) Above 100% of median income', fontsize=10)
    plt.title('Scatter Plot of Education vs Income of Women for Each Country')

    country_handles = []

    for country in countries:
        for j in range(len(result_education[country])):
            if education_levels_e[0] == result_education[country][j][0]:
                education_value = float(result_education[country][j][1])

                income_value = [result_income[country][i][1] for i in range(len(result_income[country])) if result_income[country][i][0] == education_levels_i[0]]

                if income_value: 
                    plt.scatter(education_value, income_value[0], color=country_colors[country], marker='o', label=country)
                
            if education_levels_e[1] == result_education[country][j][0]:
                education_value = float(result_education[country][j][1])

                income_value = [result_income[country][i][1] for i in range(len(result_income[country])) if result_income[country][i][0] == education_levels_i[1]]

                if income_value:
                    plt.scatter(education_value, income_value[0], color=country_colors[country], marker='D')

            if education_levels_e[2] == result_education[country][j][0]:
                education_value = float(result_education[country][j][1])

                income_value = [result_income[country][i][1] for i in range(len(result_income[country])) if result_income[country][i][0] == education_levels_i[2]]

                if income_value: 
                    plt.scatter(education_value, income_value[0], color=country_colors[country], marker='v')    

    country_handles = [Line2D([0], [0], marker='s', color='w', markerfacecolor=color, markersize=10, label=country) for country, color in country_colors.items()]
    all_handles = country_handles + legend_handles_education

    plt.legend(handles=all_handles, title='Legend', loc='upper right', ncol=1, handleheight=1.4, labelspacing=0.7, fontsize=8)

    plt.tight_layout()
    plt.tight_layout()
    plt.show()
    



file_name_education = './data/education_unfiltered.csv'
file_name_income = './data/income_unfiltered.csv'

countries_list = ['Austria', 'Czechia', 'Denmark', 'Korea', 'Norway', 'Portugal']
education_values_list_e = ['Primary education', 'Upper secondary education', 'Bachelor\'s, Master\'s and Doctoral or equivalent level']
education_values_list_i = ['Below upper secondary education', 'Upper secondary education', 'Upper secondary education', 'Bachelor\'s, master\'s, doctoral or equivalent level']

result_education = extract_countries_and_values(file_name_education, 'Reference area', countries_list, 'Education level', education_values_list_e, 'OBS_VALUE', '',  'TIME_PERIOD', delimiter=',', encoding='utf-8')
result_income = extract_countries_and_values(file_name_income, 'Reference area', countries_list, 'Educational attainment level', education_values_list_i, 'OBS_VALUE', 'Income', 'TIME_PERIOD', delimiter=',', encoding='utf-8')

solve_data(result_education, result_income)
