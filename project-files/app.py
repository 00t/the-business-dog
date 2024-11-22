import streamlit as st
from valuation_logic import monte_carlo_valuation
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# App Title
st.title("The Business Dog")
st.subheader("Discover Your Business's Fair Market Value")

# Sidebar Inputs
st.sidebar.header("Input Parameters")
fcf = st.sidebar.number_input("Free Cash Flow (FCF)", value=100000.0)
growth_rate_low = st.sidebar.slider("Growth Rate (Low)", 0.0, 0.2, 0.05)
growth_rate_high = st.sidebar.slider("Growth Rate (High)", 0.0, 0.3, 0.1)
discount_rate = st.sidebar.slider("Discount Rate", 0.01, 0.15, 0.1)
terminal_rate = st.sidebar.slider("Terminal Growth Rate", 0.0, 0.05, 0.02)
iterations = 1000  # Fixed for simplicity

# Move calculation button logic to sidebar setup
if 'fcf' in st.session_state:  # Store base inputs in session state
    tab1, tab2, tab3 = st.tabs(["Market Position", "Growth Projections", "Detailed Analysis"])
    
    with tab1:
        # Perform Monte Carlo Simulation
        results = monte_carlo_valuation(
            fcf=fcf,
            growth_rate=(growth_rate_low, growth_rate_high),
            discount_rate=discount_rate,
            terminal_rate=terminal_rate,
            iterations=iterations,
        )
        
        # Extract key metrics
        mean_valuation = results["mean"]
        competitor_values = st.session_state.competitor_values

        # Generate random competitor values with good spread
        competitor_values = [
            mean_valuation * np.random.uniform(0.7, 1.3) for _ in range(5)
        ]

        # Create Semi-Circle Chart with improved styling
        fig, ax = plt.subplots(figsize=(12, 6), facecolor='#0E1117')
        ax.set_xlim(-1.7, 1.7)
        ax.set_ylim(-0.2, 1.3)
        
        theta = np.linspace(0, np.pi, 100)
        x = np.cos(theta)
        y = np.sin(theta)
        
        # Add subtle grid lines
        for i in np.linspace(0.2, 1, 4):
            ax.plot(x*i, y*i, '--', color='#2C3138', linewidth=0.8, zorder=1)
        
        # Main semi-circle with gradient and increased thickness
        colors = ['#48CAE4', '#00B4D8', '#0096C7', '#0077B6', '#023E8A']
        for i, color in enumerate(colors):
            offset = i * 0.02  # Increased offset for more visible layers
            ax.plot(x, y-offset, color=color, linewidth=20, alpha=0.6, zorder=2)  # Thicker lines
        
        # Calculate positions for markers
        all_values = competitor_values + [mean_valuation]
        min_val, max_val = min(all_values), max(all_values)
        base_angle = 0.3
        
        # Your business marker
        relative_pos = (mean_valuation - min_val) / (max_val - min_val) if max_val != min_val else 0.5
        angle = np.pi * (0.5 + (relative_pos - 0.5) * base_angle)
        marker_x = np.cos(angle)
        marker_y = np.sin(angle)
        
        # Add glow effect to your marker
        ax.plot(marker_x, marker_y, 'o', markersize=20, color='#90E0EF', alpha=0.3, zorder=3)
        ax.plot(marker_x, marker_y, 'o', markersize=15, color='#90E0EF', alpha=0.6, zorder=4)
        ax.plot(marker_x, marker_y, 'o', markersize=10, color='#90E0EF', label="Your Business", zorder=5)
        
        # Add value label
        ax.text(marker_x, marker_y + 0.15, f"Your Business\n${mean_valuation:,.0f}", 
                ha="center", va="center", fontsize=10, fontweight='bold', color='white',
                bbox=dict(facecolor='#1E232B', edgecolor='#90E0EF', alpha=0.8, pad=3))
        
        # Plot competitors
        competitor_colors = ['#CAF0F8', '#90E0EF', '#00B4D8', '#0077B6', '#03045E']
        for i, (comp_value, color) in enumerate(zip(competitor_values, competitor_colors)):
            relative_pos = (comp_value - min_val) / (max_val - min_val) if max_val != min_val else 0.5
            angle = np.pi * (0.5 + (relative_pos - 0.5) * base_angle)
            comp_marker_x = np.cos(angle)
            comp_marker_y = np.sin(angle)
            
            # Add competitor markers with glow
            ax.plot(comp_marker_x, comp_marker_y, 'o', markersize=16, color=color, alpha=0.3, zorder=3)
            ax.plot(comp_marker_x, comp_marker_y, 'o', markersize=12, color=color, alpha=0.6, zorder=4)
            ax.plot(comp_marker_x, comp_marker_y, 'o', markersize=8, color=color, 
                    label=f"Competitor {i + 1}", zorder=5)
            
            # Add value labels
            ax.text(comp_marker_x, comp_marker_y - 0.15, f"Competitor {i+1}\n${comp_value:,.0f}", 
                    ha="center", va="center", fontsize=9, color='white',
                    bbox=dict(facecolor='#1E232B', edgecolor=color, alpha=0.8, pad=3))

        # Add legend
        legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
                          ncol=3, frameon=False, fontsize=10)
        plt.setp(legend.get_texts(), color='white')
        
        ax.axis("off")
        ax.set_title("Market Position Comparison", pad=20, fontsize=14, fontweight='bold', color='white')
        
        plt.tight_layout()
        st.pyplot(fig)

        # Summary Section
        st.subheader("Comparison")
        st.write("Compare your business valuation with similar competitors in the market.")

    with tab2:
        # Scenario toggle now updates automatically
        scenario = st.radio(
            "Select Scenario",
            ["Conservative", "Expected", "Optimistic"],
            horizontal=True,
            key='scenario_toggle'  # Add key for session state
        )
        
        # Define growth scenarios
        growth_scenarios = {
            "Conservative": {
                "growth": st.session_state.growth_rate_low,
                "color": "#FF6B6B",
                "fcf_multiplier": 8
            },
            "Expected": {
                "growth": (st.session_state.growth_rate_high + st.session_state.growth_rate_low) / 2,
                "color": "#4ECDC4",
                "fcf_multiplier": 10
            },
            "Optimistic": {
                "growth": st.session_state.growth_rate_high,
                "color": "#48CAE4",
                "fcf_multiplier": 12
            }
        }
        
        # Calculate projections
        projection_years = 5
        years = list(range(projection_years + 1))
        
        selected_growth = growth_scenarios[scenario]["growth"]
        selected_color = growth_scenarios[scenario]["color"]
        selected_multiplier = growth_scenarios[scenario]["fcf_multiplier"]
        
        # Calculate base projections
        fcf_projections = [fcf * (1 + selected_growth) ** year for year in years]
        
        # Calculate valuations using both DCF and multiple methods
        dcf_valuations = []
        multiple_valuations = []
        
        for projected_fcf in fcf_projections:
            # DCF Valuation
            terminal_value = projected_fcf * (1 + terminal_rate) / (discount_rate - terminal_rate)
            dcf_val = terminal_value / (1 + discount_rate)
            dcf_valuations.append(dcf_val)
            
            # Multiple-based Valuation
            multiple_val = projected_fcf * selected_multiplier
            multiple_valuations.append(multiple_val)
        
        # Create enhanced line chart
        fig = go.Figure()
        
        # Add FCF line
        fig.add_trace(go.Scatter(
            x=years,
            y=fcf_projections,
            name='Free Cash Flow',
            line=dict(color=selected_color, width=3, dash='dot'),
            hovertemplate='Year %{x}<br>FCF: $%{y:,.0f}<extra></extra>'
        ))
        
        # Add DCF Valuation line
        fig.add_trace(go.Scatter(
            x=years,
            y=dcf_valuations,
            name='DCF Valuation',
            line=dict(color=selected_color, width=3),
            hovertemplate='Year %{x}<br>DCF Value: $%{y:,.0f}<extra></extra>'
        ))
        
        # Add Multiple-based Valuation line
        fig.add_trace(go.Scatter(
            x=years,
            y=multiple_valuations,
            name='Multiple-based Value',
            line=dict(color=selected_color, width=3, dash='dash'),
            hovertemplate='Year %{x}<br>Multiple Value: $%{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=f"{scenario} Growth Scenario Analysis",
            xaxis_title="Years from Now",
            yaxis_title="Amount ($)",
            plot_bgcolor='#0E1117',
            paper_bgcolor='#0E1117',
            font=dict(color='white'),
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
                bgcolor='rgba(0,0,0,0)'
            ),
            yaxis=dict(
                gridcolor='#2C3138',
                zerolinecolor='#2C3138',
                type='log'  # Log scale for better visualization of growth
            ),
            xaxis=dict(
                gridcolor='#2C3138',
                zerolinecolor='#2C3138',
                tickmode='array',
                ticktext=['Now'] + [f'Year {i}' for i in range(1, projection_years + 1)],
                tickvals=years
            ),
            hovermode='x unified',
            margin=dict(t=50, l=50, r=50, b=50)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add detailed metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "5-Year FCF", 
                f"${fcf_projections[-1]:,.0f}",
                f"{((fcf_projections[-1]/fcf - 1) * 100):,.1f}%"
            )
        with col2:
            st.metric(
                "DCF Valuation", 
                f"${dcf_valuations[-1]:,.0f}",
                f"{((dcf_valuations[-1]/dcf_valuations[0] - 1) * 100):,.1f}%"
            )
        with col3:
            st.metric(
                "Multiple Valuation", 
                f"${multiple_valuations[-1]:,.0f}",
                f"{((multiple_valuations[-1]/multiple_valuations[0] - 1) * 100):,.1f}%"
            )
        
        # Add scenario insights
        st.write(f"""
        **{scenario} Scenario Analysis:**
        - Annual Growth Rate: {selected_growth:.1%}
        - FCF Multiple: {selected_multiplier}x
        - DCF Terminal Rate: {terminal_rate:.1%}
        - Discount Rate: {discount_rate:.1%}
        """)
        
        # Add risk factors
        st.info("""
        **Key Considerations:**
        - DCF valuation assumes stable long-term growth
        - Multiple-based valuation reflects market comparables
        - Actual results may vary based on market conditions and execution
        """)

    with tab3:
        st.header("Valuation Build-up Analysis")
        
        # Get Monte Carlo results
        results = monte_carlo_valuation(
            fcf=st.session_state.fcf,
            growth_rate=(st.session_state.growth_rate_low, st.session_state.growth_rate_high),
            discount_rate=st.session_state.discount_rate,
            terminal_rate=st.session_state.terminal_rate,
            iterations=1000
        )
        
        # Calculate waterfall components
        base_fcf = st.session_state.fcf
        mean_growth = (st.session_state.growth_rate_high + st.session_state.growth_rate_low) / 2
        
        # Waterfall components
        base_value = base_fcf * 5
        growth_impact = base_fcf * mean_growth * 10
        market_risk = base_fcf * mean_growth * 2
        size_adjustment = -base_fcf * 0.5
        risk_factors = -base_fcf * mean_growth * 3
        final_value = results['mean']
        
        components = {
            "Base Value": base_value,
            "Growth Impact": growth_impact,
            "Market Risk": market_risk,
            "Size Adjustment": size_adjustment,
            "Risk Factors": risk_factors,
            "Final Value": final_value
        }
        
        # Create waterfall chart
        fig = go.Figure(go.Waterfall(
            name="Valuation Build-up",
            orientation="v",
            measure=["relative", "relative", "relative", "relative", "relative", "total"],
            x=list(components.keys()),
            y=list(components.values()),
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            decreasing={"marker": {"color": "#FF6B6B"}},
            increasing={"marker": {"color": "#4ECDC4"}},
            totals={"marker": {"color": "#48CAE4"}},
            text=[f"${x:,.0f}" for x in components.values()],
            textposition="outside"
        ))
        
        # Update layout
        fig.update_layout(
            title={
                'text': "Valuation Build-up Analysis",
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            showlegend=False,
            plot_bgcolor='#0E1117',
            paper_bgcolor='#0E1117',
            font=dict(color='white'),
            yaxis=dict(
                gridcolor='#2C3138',
                zerolinecolor='#2C3138',
                title="Value ($)"
            ),
            xaxis=dict(
                gridcolor='#2C3138',
                title=""
            ),
            height=600,
            margin=dict(t=100)
        )
        
        # Display waterfall chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Display key statistics
        st.subheader("Valuation Summary")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Base Value", 
                f"${base_value:,.0f}",
                f"{(growth_impact/base_value):+.1%} Growth Impact"
            )
        
        with col2:
            st.metric(
                "Final Valuation", 
                f"${final_value:,.0f}",
                f"{(final_value/base_value - 1):+.1%} Total Change"
            )
        
        # Add explanation
        st.caption("""
        This analysis shows how different factors contribute to the final valuation:
        - Base Value: Initial valuation using conservative multiple
        - Growth Impact: Additional value from projected growth
        - Market Risk: Adjustment for market conditions
        - Size Adjustment: Adjustment for company size
        - Risk Factors: Discount for company-specific risks
        - Final Value: Resulting valuation from Monte Carlo simulation
        """)

# In sidebar, store initial inputs in session state
with st.sidebar:
    if st.button("Initialize Valuation"):
        # Set random seed for consistency
        np.random.seed(42)
        
        # Store base values in session state
        st.session_state.fcf = fcf
        st.session_state.growth_rate_low = growth_rate_low
        st.session_state.growth_rate_high = growth_rate_high
        st.session_state.discount_rate = discount_rate
        st.session_state.terminal_rate = terminal_rate
        
        # Generate and store competitor values once
        if 'competitor_values' not in st.session_state:
            st.session_state.competitor_values = [
                fcf * np.random.uniform(0.9, 1.1) for _ in range(5)
            ]
