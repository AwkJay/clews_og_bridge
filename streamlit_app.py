import streamlit as st
import httpx
import json
import pandas as pd

st.set_page_config(page_title="CLEWS → OG-Core Bridge | Demo", layout="wide")

st.markdown("""
<style>
/* Clean color scheme with teal accent hashtag 01696f */
:root {
  --primary-color: #01696f;
}
</style>
""", unsafe_allow_html=True)

st.title("CLEWS → OG-Core Bridge | Demo")

# Sidebar
st.sidebar.header("Configuration")
api_url = st.sidebar.text_input("API URL", "http://localhost:8000")
scenario = st.sidebar.text_input("Scenario", "mauritius_baseline")
run_id = st.sidebar.text_input("Run ID", "demo_001")
country = st.sidebar.text_input("Country", "Mauritius")

# Health check
@st.cache_data(ttl=10)
def check_health(api_url: str) -> bool:
    try:
        with httpx.Client(timeout=5.0) as client:
            return client.get(f"{api_url}/health").status_code == 200
    except httpx.RequestError:
        return False

is_healthy = check_health(api_url)
if is_healthy:
    st.sidebar.markdown('🟢 API is reachable')
else:
    st.sidebar.markdown('🔴 API not reachable')
    st.warning("API is not reachable. Please start the API by running: `uvicorn main:app --reload --port 8000`")

# Main Area
st.subheader("Upload CLEWS CSV Outputs")

col1, col2, col3 = st.columns(3)

with col1:
    cost_file = st.file_uploader("Total Discounted Cost", type=['csv'])
with col2:
    tech_activity_file = st.file_uploader("Total Annual Technology Activity", type=['csv'])
with col3:
    emissions_file = st.file_uploader("Annual Emissions", type=['csv'])

can_run = cost_file is not None and tech_activity_file is not None and emissions_file is not None

if st.button("Run Pipeline", disabled=not can_run, type="primary"):
    with st.spinner("Running pipeline..."):
        try:
            files = {
                "total_discounted_cost": (cost_file.name, cost_file.getvalue(), "text/csv"),
                "total_annual_technology_activity": (tech_activity_file.name, tech_activity_file.getvalue(), "text/csv"),
                "annual_emissions": (emissions_file.name, emissions_file.getvalue(), "text/csv"),
            }
            data = {
                "scenario": scenario,
                "run_id": run_id,
                "country": country
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(f"{api_url}/transform", files=files, data=data)
            
            if response.status_code == 200:
                st.success("Pipeline ran successfully!")
                st.session_state["result"] = response.json()
                    
            else:
                st.error(f"Error {response.status_code}: {response.text}")
                
        except httpx.RequestError as e:
            st.error(f"Failed to connect to API: {e}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

if "result" in st.session_state:
    result = st.session_state["result"]
    
    tab1, tab2, tab3, tab4 = st.tabs(["Mapping Trace", "OG-Core Parameters", "CLEWS Summary", "JSON"])
    
    with tab1:
        trace = result.get("og_parameters", {}).get("mapping_trace", {})
        for param_key, param_info in trace.items():
            with st.expander(f"Parameter: {param_key}"):
                st.write(f"**Source Variable:** {param_info.get('source_variable')}")
                st.write(f"**Transformation:** {param_info.get('transformation_type', '')} / {param_info.get('formula', '')}")
                st.write(f"**Aggregation:** {param_info.get('aggregation_rule')}")
                st.write(f"**Elasticity:** {param_info.get('elasticity_used', 'N/A')}")
                st.write(f"**Description:** {param_info.get('parameter_role', '')}")
    
    with tab2:
        params = result.get("og_parameters", {}).get("parameters", {})
        for param_key, param_data in params.items():
            st.markdown(f"#### {param_key}")
            st.caption(f"{param_data.get('og_core_meaning')} | Units: {param_data.get('units')}")
            values = param_data.get("value", {})
            
            # Prepare data for line chart
            plot_data = []
            for industry, years_data in values.items():
                for year, val in years_data.items():
                    plot_data.append({"Industry": industry, "Year": year, "Value": val})
            
            if plot_data:
                df_plot = pd.DataFrame(plot_data)
                df_pivot = df_plot.pivot(index="Year", columns="Industry", values="Value")
                st.line_chart(df_pivot)
                with st.expander("Show Data"):
                    st.dataframe(df_pivot)
    
    with tab3:
        clews_outputs = result.get("clews_outputs", {}).get("data", {})
        for var_name, var_data in clews_outputs.items():
            st.markdown(f"#### {var_name}")
            rows = []
            for tech, years_data in var_data.items():
                row = {"Technology": tech}
                row.update(years_data)
                rows.append(row)
            if rows:
                st.dataframe(pd.DataFrame(rows))
    
    with tab4:
        st.code(json.dumps(result, indent=2), language="json")
        st.download_button("Download JSON", data=json.dumps(result, indent=2), file_name="clews_og_bridge_output.json", mime="application/json")

st.markdown("---")
st.subheader("Run History")
try:
    with httpx.Client(timeout=5.0) as client:
        hist_resp = client.get(f"{api_url}/history")
        if hist_resp.status_code == 200:
            history = hist_resp.json()
            if history:
                st.dataframe(pd.DataFrame(history))
            else:
                st.info("No run history available.")
        else:
            st.warning("Could not fetch history.")
except httpx.RequestError:
    st.info("API is not available to fetch history.")
