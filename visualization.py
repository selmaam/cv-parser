import streamlit as st
import plotly.graph_objects as go
import pandas as pd 
import numpy as np

def plot_subcategory_skills(result, threshold=2, chart_width=600):
    # Count inner skills for each subcategory
    subcategory_counts = {}
    for category, subcategories in result.items():
        for subcategory, skills_data in subcategories.items():
            subcategory_counts[subcategory] = len(skills_data)

    # Filter subcategories based on threshold
    filtered_subcategories = {subcategory: count for subcategory, count in subcategory_counts.items() if count >= threshold}

    # Display bar chart for filtered subcategories with adjusted width
    if filtered_subcategories:
        df = pd.DataFrame(list(filtered_subcategories.items()), columns=['Subcategory', 'Count'])
        fig = px.bar(df, x='Subcategory', y='Count', color='Count', color_continuous_scale='Reds', 
                     title='Subcategory Skills Count', width=chart_width)
        fig.update_layout(xaxis_title='Subcategory', yaxis_title='Count', coloraxis_showscale=False)
        st.plotly_chart(fig)


def create_pie_chart(df):
    # Ensure the DataFrame is not empty
        fig = px.pie(df, names='Skill', title='Skill Distribution')
        fig.update_traces(textposition='inside', textinfo='percent+label')  # Customize text position and info
        st.plotly_chart(fig, use_container_width=True)



def find_skill_in_categories(data, skills_dict):
    if data is None or 'categories' not in data:
        st.error("Invalid data format or data is None")
        return {}

    found_skills = {}
    for category_data in data['categories']:
        category_name = category_data['name']
        subcategories = category_data.get('subcategories', {})
        
        for subcategory_data in subcategories.values():
            subcategory_name = subcategory_data['name']
            for item in subcategory_data['items']:
                skill_name = item['name']
                
                for skill_key, skill_score in skills_dict.items():
                    # Ensure skill_key is a string before comparison
                    if isinstance(skill_key, str) and skill_name.lower() in skill_key.lower():
                        if category_name not in found_skills:
                            found_skills[category_name] = {}
                        if subcategory_name not in found_skills[category_name]:
                            found_skills[category_name][subcategory_name] = []
                        found_skills[category_name][subcategory_name].append({
                            'name': skill_key,
                            'score': skill_score
                        })
    return found_skills


import plotly.express as px

def plot_skills_chart(df, chart_type='pie', top_n=10):
    # Get the top skills
    top_skills = df['name'].value_counts().head(top_n)
    
    if chart_type == 'pie':
        fig = px.pie(names=top_skills.index, values=top_skills.values, title='Top Skills Pie Chart')
    elif chart_type == 'treemap':
        fig = px.treemap(names=top_skills.index, values=top_skills.values, title='Top Skills Treemap')
    else:
        st.error('Invalid chart type. Please choose either "pie" or "treemap".')
        return
    
    # Display the chart
    st.plotly_chart(fig)
    

def visualize_tree_map(categories, subcategories, skills_list):
    # Create a DataFrame from the data
    data = {'Category': categories, 'Subcategory': subcategories, 'Skill': skills_list}
    df = pd.DataFrame(data)

    # Aggregate the data for visualization
    agg_df = df.groupby(['Category', 'Subcategory', 'Skill']).size().reset_index(name='Count')

    # Create the tree map
    fig = px.treemap(agg_df, path=['Category', 'Subcategory', 'Skill'], values='Count', color='Count',
                     color_continuous_scale='viridis',
                     hover_data={'Skill': True, 'Count': False})
    
    # Ensure the colors reflect different counts properly
    color_midpoint = agg_df['Count'].mean()
    fig.update_traces(marker=dict(cmid=color_midpoint))

    # Hide the color scale if desired
    fig.update_layout(coloraxis_showscale=False)

    # Display the tree map in Streamlit
    st.plotly_chart(fig)
    
    
    
import streamlit as st
import pandas as pd
import plotly.express as px

def display_skills_distribution(skills_from_resume, skills_from_job_desc):
    """
    Display the distribution of skills from the resume and their match with the job description.

    Parameters:
    skills_from_resume (pd.DataFrame): DataFrame containing skills from the resume.
    skills_from_job_desc (pd.DataFrame): DataFrame containing skills from the job description.
    """
    # Extract the skills columns
    skills_res = skills_from_resume['skills'].tolist()
    skills_job = skills_from_job_desc['full'].tolist()
    
    # Find common and unique skills
    common_skills = set(skills_res).intersection(set(skills_job))
    unique_job_skills = set(skills_job) - common_skills
    
    custom_reds = ['#8a2101', '#f22213', '#CD5C5C']

    # Create a DataFrame for the pie chart
    skills_data = {
        'Category': ['Common Skills', 'Unique Job Skills'],
        'Count': [len(common_skills), len(unique_job_skills)]
    }
    skills_df = pd.DataFrame(skills_data)

    # Create the pie chart with shades of red
    fig_pie = px.pie(
        skills_df, 
        names='Category', 
        values='Count', 
        title='Skills Distribution',
        color_discrete_sequence=custom_reds
    )

    return fig_pie

def plot_matches_pie(number_of_resumes, number_of_matches):
    """
    Create a pie chart showing the proportion of matches and non-matches.

    Parameters:
    number_of_resumes (int): Total number of resumes.
    number_of_matches (int): Number of resumes that were matched.

    Returns:
    fig_pie (plotly.graph_objs.Figure): Pie chart showing matches vs. non-matches.
    """
    # Create a DataFrame for the pie chart data
    pie_data = {'Category': ['Resume Matched', 'Resume Non-Matched'],
                'Count': [number_of_matches, number_of_resumes - number_of_matches]}
    pie_df = pd.DataFrame(pie_data)

    # Create the pie chart using Plotly
    fig_pie = px.pie(pie_df, values='Count', names='Category',
                     title='Proportion of Matches vs. Non-Matches',
                     color_discrete_sequence=px.colors.qualitative.Plotly)

    return fig_pie