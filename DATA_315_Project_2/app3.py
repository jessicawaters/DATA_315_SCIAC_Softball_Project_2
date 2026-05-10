import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="SCIAC Softball Dashboard",
    layout="wide"
)

# ============================================
# LOAD DATA
# ============================================
@st.cache_data
def load_data():

    df_games = pd.read_csv("data/clean_softball_data.csv")
    df_teams = pd.read_csv("data/team_summary.csv")

    # Extra school information
    extra_data = [
        {"team": "california-lutheran", "acceptance_rate": 76, "tuition": 53650, "coach_changes": 2},
        {"team": "occidental", "acceptance_rate": 44, "tuition": 70492, "coach_changes": 3},
        {"team": "whittier", "acceptance_rate": 83, "tuition": 51917, "coach_changes": 2},
        {"team": "pomona-pitzer", "acceptance_rate": 14.5, "tuition": 81577, "coach_changes": 1},
        {"team": "la-verne", "acceptance_rate": 48.5, "tuition": 49550, "coach_changes": 3},
        {"team": "chapman", "acceptance_rate": 65, "tuition": 69990, "coach_changes": 1},
        {"team": "redlands", "acceptance_rate": 83, "tuition": 61932, "coach_changes": 1}
    ]

    extra_df = pd.DataFrame(extra_data)

    df_teams = df_teams.merge(
        extra_df,
        on="team",
        how="left"
    )

    return df_games, df_teams


df_games, df_teams = load_data()

# ============================================
# CLEAN DATA
# ============================================

df_games["year"] = pd.to_numeric(
    df_games["year"],
    errors="coerce"
)

df_games = df_games.dropna(
    subset=["year"]
)

df_games["year"] = df_games["year"].astype(int)

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_team_year_stats(team, year=None):

    data = df_games[df_games["team"] == team]

    if year:
        data = data[data["year"] == year]

    if len(data) == 0:
        return None

    return {
        "games": len(data),
        "wins": int(data["win_flag"].sum()),
        "win_pct": data["win_flag"].mean(),
        "runs_for": data["score_for"].mean(),
        "runs_against": data["score_against"].mean(),
        "run_diff": data["score_for"].mean() - data["score_against"].mean()
    }


def get_team_info(team):

    result = df_teams[df_teams["team"] == team]

    if len(result) == 0:
        return None

    return result.iloc[0]


def stability_label(changes):

    if changes == 1:
        return "High"

    elif changes == 2:
        return "Medium"

    return "Low"


def calculate_stability_score(team):

    team_info = get_team_info(team)

    if team_info is None:
        return 0

    coaching_score = (4 - team_info["coach_changes"]) / 3

    yearly_wins = (
        df_games[df_games["team"] == team]
        .groupby("year")["win_flag"]
        .mean()
    )

    if len(yearly_wins) == 0 or yearly_wins.mean() == 0:
        consistency = 0

    else:
        consistency = 1 - (
            yearly_wins.std() / yearly_wins.mean()
        )

        consistency = max(0, min(1, consistency))

    early = yearly_wins[
        yearly_wins.index < 2022
    ].mean()

    recent = yearly_wins[
        yearly_wins.index >= 2022
    ].mean()

    if pd.isna(early):
        early = 0

    if pd.isna(recent):
        recent = 0

    trajectory = (
        (recent - early)
        if early > 0
        else recent
    )

    trajectory = max(-1, min(1, trajectory))
    trajectory = (trajectory + 1) / 2

    score = (
        coaching_score * 0.4
        + consistency * 0.3
        + trajectory * 0.3
    )

    return score

# ============================================
# SIDEBAR
# ============================================

st.sidebar.header("Dashboard Filters")

all_teams = sorted(
    df_games["team"].unique()
)

selected_teams = st.sidebar.multiselect(
    "Select Team(s)",
    options=all_teams,
    default=[all_teams[0]],
    max_selections=2
)

years_list = sorted(
    df_games["year"].unique()
)

year_options = ["All Years"] + [
    str(y) for y in years_list
]

selected_year_str = st.sidebar.selectbox(
    "Select Year",
    options=year_options
)

selected_year = (
    None
    if selected_year_str == "All Years"
    else int(selected_year_str)
)

# ============================================
# TITLE
# ============================================

st.title("SCIAC Softball Dashboard")

st.markdown("""
Interactive dashboard analyzing SCIAC softball performance,
program stability, and institutional trends from 2019–2025.
""")

st.divider()

# ============================================
# TABS
# ============================================

tab1, tab2, tab3, tab4 = st.tabs([
    "Team Explorer",
    "Head-to-Head",
    "Conference & Insights",
    "Datasets"
])

# ============================================
# TAB 1: TEAM OVERVIEW
# ============================================
with tab1:

    if len(selected_teams) == 1:

        team = selected_teams[0]

        team_info = get_team_info(team)

        stats = get_team_year_stats(team, selected_year)

        if stats and team_info is not None:

            st.subheader(
                f"{team.replace('-', ' ').title()} Overview"
            )

            # ============================================
            # TOP METRICS
            # ============================================

            metric1, metric2, metric3, metric4 = st.columns(4)

            with metric1:
                st.metric(
                    "Win %",
                    f"{stats['win_pct']:.1%}"
                )

            with metric2:
                st.metric(
                    "Games",
                    stats["games"]
                )

            with metric3:
                st.metric(
                    "Run Differential",
                    f"{stats['run_diff']:.2f}"
                )

            with metric4:
                st.metric(
                    "Coach Changes",
                    int(team_info["coach_changes"]),
                    delta=stability_label(
                        team_info["coach_changes"]
                    )
                )

            # ============================================
            # MAIN VISUALS
            # ============================================

            left_col, right_col = st.columns(2)

            # --------------------------------------------
            # WIN TREND
            # --------------------------------------------

            with left_col:

                st.subheader("Yearly Win % Trend")

                yearly_data = (
                    df_games[df_games["team"] == team]
                    .groupby("year")
                    .agg({"win_flag": "mean"})
                    .reset_index()
                )

                yearly_data.columns = ["Year", "Win %"]

                fig_yearly = px.line(
                    yearly_data,
                    x="Year",
                    y="Win %",
                    markers=True
                )

                fig_yearly.add_hline(
                    y=0.5,
                    line_dash="dash",
                    line_color="gray"
                )

                fig_yearly.update_layout(
                    height=350,
                    margin=dict(
                        l=10,
                        r=10,
                        t=40,
                        b=10
                    )
                )

                st.plotly_chart(
                    fig_yearly,
                    use_container_width=True
                )

            # --------------------------------------------
            # MAP
            # --------------------------------------------

            with right_col:

                st.subheader("Program Location")

                map_data = pd.DataFrame([{
                    "team": team_info["team"],
                    "lat": team_info["lat"],
                    "lon": team_info["lon"]
                }])

                fig_map = px.scatter_mapbox(
                    map_data,
                    lat="lat",
                    lon="lon",
                    hover_name="team",
                    zoom=6
                )

                fig_map.update_layout(
                    mapbox_style="carto-positron",
                    height=350,
                    margin=dict(
                        l=10,
                        r=10,
                        t=40,
                        b=10
                    )
                )

                st.plotly_chart(
                    fig_map,
                    use_container_width=True
                )

            # ============================================
            # SCHOOL INFO
            # ============================================

            with st.expander("School Information"):

                school_df = pd.DataFrame({
                    "Category": [
                        "Enrollment",
                        "Acceptance Rate",
                        "Tuition"
                    ],
                    "Value": [
                        f"{int(team_info['enrollment']):,}",
                        f"{team_info['acceptance_rate']:.1f}%",
                        f"${int(team_info['tuition']):,}"
                    ]
                })

                st.dataframe(
                    school_df,
                    use_container_width=True,
                    hide_index=True
                )

        else:

            st.error(
                "No data available for selected team."
            )

    elif len(selected_teams) == 2:

        st.info(
            "Select one team for overview. "
            "Use Head-to-Head for comparisons."
        )

    else:

        st.warning(
            "Please select a team."
        )
# ============================================
# TAB 2 — HEAD TO HEAD
# ============================================

with tab2:

    if len(selected_teams) == 2:

        team1, team2 = selected_teams

        stats1 = get_team_year_stats(
            team1,
            selected_year
        )

        stats2 = get_team_year_stats(
            team2,
            selected_year
        )

        st.subheader(
            f"{team1.replace('-', ' ').title()} vs "
            f"{team2.replace('-', ' ').title()}"
        )

        # ====================================
        # TOP METRICS
        # ====================================

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                f"{team1.replace('-', ' ').title()} Win %",
                f"{stats1['win_pct']:.1%}"
            )

        with col2:
            st.metric(
                f"{team2.replace('-', ' ').title()} Win %",
                f"{stats2['win_pct']:.1%}"
            )

        with col3:
            st.metric(
                "Difference",
                f"{abs(stats1['win_pct'] - stats2['win_pct']):.1%}"
            )

        st.divider()

        # ====================================
        # OFFENSE VS DEFENSE
        # ====================================

        comparison_data = pd.DataFrame({
            "Team": [
                team1.replace("-", " ").title(),
                team2.replace("-", " ").title()
            ],
            "Runs Scored": [
                stats1["runs_for"],
                stats2["runs_for"]
            ],
            "Runs Allowed": [
                stats1["runs_against"],
                stats2["runs_against"]
            ]
        })

        fig_comp = go.Figure()

        fig_comp.add_trace(
            go.Bar(
                name="Runs Scored",
                x=comparison_data["Team"],
                y=comparison_data["Runs Scored"]
            )
        )

        fig_comp.add_trace(
            go.Bar(
                name="Runs Allowed",
                x=comparison_data["Team"],
                y=comparison_data["Runs Allowed"]
            )
        )

        fig_comp.update_layout(
            barmode="group",
            title="Offense vs Defense",
            height=450
        )

        st.plotly_chart(
            fig_comp,
            use_container_width=True
        )

        st.divider()

        # ============================================
        # RECENT MATCHUPS
        # ============================================

        st.subheader("Recent Matchup Results")

        matchup_games = df_games[
            (
                    ((df_games["team"] == team1) &
                     (df_games["opponent"] == team2))
                    |
                    ((df_games["team"] == team2) &
                     (df_games["opponent"] == team1))
            )
        ].copy()

        # Remove duplicate games
        if "date" in matchup_games.columns:
            matchup_games["game_id"] = (
                    matchup_games["date"].astype(str)
                    + "_"
                    + matchup_games[["team", "opponent"]].min(axis=1)
                    + "_"
                    + matchup_games[["team", "opponent"]].max(axis=1)
            )

            matchup_games = matchup_games.drop_duplicates(
                subset="game_id"
            )

        matchup_games = matchup_games.sort_values(
            by="date",
            ascending=False
        )

        recent_games = matchup_games.head(9)

        # Count wins correctly from outcomes
        team1_recent_wins = len(
            recent_games[
                recent_games["outcome"] == "W"
                ]
        )

        team2_recent_wins = len(
            recent_games[
                recent_games["outcome"] == "L"
                ]
        )

        recent_df = pd.DataFrame({
            "Team": [
                team1.replace("-", " ").title(),
                team2.replace("-", " ").title()
            ],
            "Wins in Last 9": [
                team1_recent_wins,
                team2_recent_wins
            ]
        })

        fig_recent = px.bar(
            recent_df,
            x="Team",
            y="Wins in Last 9",
            text="Wins in Last 9",
            title="Wins in Last 9 Matchups"
        )

        fig_recent.update_traces(
            textposition="outside"
        )

        fig_recent.update_layout(
            yaxis=dict(range=[0, 9]),
            showlegend=False
        )

        st.plotly_chart(
            fig_recent,
            use_container_width=True
        )

# ============================================
# TAB 3 — CONFERENCE & INSIGHTS
# ============================================

with tab3:

    # ====================================
    # CONFERENCE VS NON-CONFERENCE
    # ====================================

    st.subheader(
        "Conference vs Non-Conference Performance"
    )

    conference_df = df_games.copy()

    conference_df["team_clean"] = (
        conference_df["team"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    conference_df["opponent_clean"] = (
        conference_df["opponent"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    sciac_teams = set(
        conference_df["team_clean"].unique()
    )

    conference_df["is_sciac"] = (
        conference_df["opponent_clean"]
        .isin(sciac_teams)
    )

    conference_df = conference_df[
        conference_df["team"] != "occidental"
    ]

    conf_stats = (
        conference_df
        .groupby(["team", "is_sciac"])["win_flag"]
        .mean()
        .reset_index()
    )

    conf_pivot = conf_stats.pivot(
        index="team",
        columns="is_sciac",
        values="win_flag"
    ).reset_index()

    conf_pivot.columns = [
        "Team",
        "Non-Conference",
        "Conference"
    ]

    fig_conf = px.bar(
        conf_pivot,
        x="Team",
        y=["Conference", "Non-Conference"],
        barmode="group",
        height=500
    )

    st.plotly_chart(
        fig_conf,
        use_container_width=True
    )

    st.divider()

    # ====================================
    # COACHING STABILITY
    # ====================================

    st.subheader(
        "Coaching Stability vs Win Percentage"
    )

    coaching_data = df_teams.copy()

    fig_coaching = px.scatter(
        coaching_data,
        x="coach_changes",
        y="win_pct",
        size="total_games",
        hover_name="team",
        title="Programs with stable coaching tend to win more games",
        height=550
    )

    st.plotly_chart(
        fig_coaching,
        use_container_width=True
    )

    st.divider()

    # ====================================
    # ENROLLMENT + TUITION
    # ====================================

    col1, col2 = st.columns(2)

    with col1:

        fig_enrollment = px.scatter(
            df_teams,
            x="enrollment",
            y="win_pct",
            hover_name="team",
            title="Enrollment vs Success",
            height=450
        )

        st.plotly_chart(
            fig_enrollment,
            use_container_width=True
        )

    with col2:

        fig_tuition = px.scatter(
            df_teams,
            x="tuition",
            y="win_pct",
            hover_name="team",
            title="Tuition vs Success",
            height=450
        )

        st.plotly_chart(
            fig_tuition,
            use_container_width=True
        )

    st.divider()

    # ====================================
    # PROGRAM STABILITY SCORE
    # ====================================

    st.subheader(
        "Program Stability Score"
    )

    df_teams["Stability Score"] = (
        df_teams["team"]
        .apply(calculate_stability_score)
    )

    fig_stability = px.bar(
        df_teams.sort_values(
            "Stability Score",
            ascending=False
        ),
        x="team",
        y="Stability Score",
        color="win_pct",
        color_continuous_scale="RdYlGn",
        height=500
    )

    st.plotly_chart(
        fig_stability,
        use_container_width=True
    )

    st.divider()

    # ====================================
    # MOMENTUM
    # ====================================

    st.subheader("Program Momentum")

    momentum_data = (
        df_games
        .groupby(["team", "year"])["win_flag"]
        .mean()
        .reset_index()
    )

    fig_momentum = px.line(
        momentum_data,
        x="year",
        y="win_flag",
        color="team",
        markers=True,
        height=550
    )

    fig_momentum.update_layout(
        yaxis_title="Win Percentage",
        xaxis_title="Year"
    )

    st.plotly_chart(
        fig_momentum,
        use_container_width=True
    )

# ============================================
# TAB 4: DATASETS (CLEAN DROPDOWN STYLE)
# ============================================

with tab4:

    st.subheader("Datasets")

    dataset_choice = st.selectbox(
        "Select Dataset",
        ["Game Data", "Team Summary", "School Info"]
    )

    if dataset_choice == "Game Data":

        st.dataframe(
            df_games,
            use_container_width=True,
            height=600
        )

    elif dataset_choice == "Team Summary":

        st.dataframe(
            df_teams,
            use_container_width=True,
            height=600
        )

    elif dataset_choice == "School Info":

        school_info = df_teams[
            [
                "team",
                "enrollment",
                "city",
                "lat",
                "lon",
                "acceptance_rate",
                "tuition",
                "coach_changes"
            ]
        ]

        st.dataframe(
            school_info,
            use_container_width=True,
            height=600
        )