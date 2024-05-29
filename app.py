import datetime
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, jsonify
from sqlalchemy import desc, or_, and_, func
import psycopg2

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456er@localhost/postgres'

db = SQLAlchemy(app)

class Championship(db.Model):
    __tablename__ = 'championships'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    league = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(255))
    matches = db.relationship('Match', backref='championship', lazy=True)

class Match(db.Model):
    __tablename__ = 'matches'
    match_id = db.Column(db.Integer, primary_key=True)
    league_id = db.Column(db.Integer, db.ForeignKey('championships.id'))
    match_date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    team_home = db.Column(db.String(100))
    team_away = db.Column(db.String(100))
    league_name = db.Column(db.String(100))
    stage = db.Column(db.String(100))
    home_score = db.Column(db.Integer)
    away_score = db.Column(db.Integer)
    home_score_ft = db.Column(db.Integer)
    away_score_ft = db.Column(db.Integer)
    total_ft = db.Column(db.Integer)
    details = db.relationship('Details', backref='match', lazy=True)

class Details(db.Model):
    __tablename__ = 'details'
    match_id = db.Column(db.Integer, db.ForeignKey('matches.match_id'), primary_key=True)
    home_q1 = db.Column(db.Integer)
    away_q1 = db.Column(db.Integer)
    home_q2 = db.Column(db.Integer)
    away_q2 = db.Column(db.Integer)
    home_q3 = db.Column(db.Integer)
    away_q3 = db.Column(db.Integer)
    home_q4 = db.Column(db.Integer)
    away_q4 = db.Column(db.Integer)
    home_ot = db.Column(db.Integer)
    away_ot = db.Column(db.Integer)
    home_win = db.Column(db.Float)
    away_win = db.Column(db.Float)
    total = db.Column(db.Float)
    handicap = db.Column(db.Float)
    hc_q1 = db.Column(db.Float)

@app.route('/')
def index():
    countries = [championship.country for championship in Championship.query.distinct(Championship.country).all()]
    return render_template('index.html', countries=countries)

@app.route('/championships/<country>')
def get_championships(country):
    championships = [championship.league for championship in Championship.query.filter_by(country=country).all()]
    return jsonify(championships)


from datetime import datetime

@app.route('/matches', methods=['POST'])
def show_matches():
    country = request.form['country']
    championship = request.form['championship']
    team_home = request.form['team_home']
    team_away = request.form['team_away']

    from_date = request.form.get('from_date', '2000-01-01') # Default to '2000-01-01' if not provided
    to_date = str(datetime.today().date()).strip()  # Convert datetime object to string
    print(from_date, to_date)
    print(country,championship,team_home,team_away)

    matches_home = Match.query.join(Championship).filter(
        (Match.league_name == championship) &
        ((Match.team_home == team_home) | (Match.team_away == team_home)) &
        (Championship.country == country) &
        (Championship.league == championship) &
        (Match.match_date > from_date)
    ).order_by(desc(Match.match_date)).all()

    matches_away = Match.query.join(Championship).filter(
        (Match.league_name == championship) &
        ((Match.team_home == team_away) | (Match.team_away == team_away)) &
        (Championship.country == country) &
        (Championship.league == championship) &
        (Match.match_date > from_date)
    ).order_by(desc(Match.match_date)).all()

    matches_between = Match.query.filter(
        or_(
            and_(Match.team_home == team_home, Match.team_away == team_away),
            and_(Match.team_home == team_away, Match.team_away == team_home)
        ),
        (Championship.country == country) &
        (Championship.league == championship) &
        (Match.match_date > from_date)
    ).order_by(desc(Match.match_date)).all()

    return render_template('matches.html', matches_home=matches_home, matches_away=matches_away,
                           matches_between=matches_between, team_home=team_home, team_away=team_away,
                           country=country, championship=championship)


@app.route('/teams/<country>/<championship>')
def get_teams(country, championship):
    championship_id = Championship.query.filter_by(country=country, league=championship).first().id
    teams_home = [match.team_home for match in Match.query.filter_by(league_id=championship_id).all()]
    teams_away = [match.team_away for match in Match.query.filter_by(league_id=championship_id).all()]
    teams = sorted(list(set(teams_home + teams_away)))  # Удаляем дубликаты команд
    return jsonify(teams)



def calculate_percentiles(country, championship, team, from_date):
    # Подключение к базе данных
    conn = psycopg2.connect(
        host="127.0.0.1",
        user="postgres",
        password="123456er",
        port="5432"
    )

    # SQL запрос для вычисления процентилей
    sql_query = f"""
        SELECT league_name, team, 
            PERCENTILE_CONT(0.0) WITHIN GROUP (ORDER BY total_ft) AS _0,
            PERCENTILE_CONT(0.05) WITHIN GROUP (ORDER BY total_ft) AS _5,
            PERCENTILE_CONT(0.1) WITHIN GROUP (ORDER BY total_ft) AS _10,
            PERCENTILE_CONT(0.15) WITHIN GROUP (ORDER BY total_ft) AS _15,
            PERCENTILE_CONT(0.2) WITHIN GROUP (ORDER BY total_ft) AS _20,
            PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY total_ft) AS _25,
            PERCENTILE_CONT(0.3) WITHIN GROUP (ORDER BY total_ft) AS _30,
            PERCENTILE_CONT(0.35) WITHIN GROUP (ORDER BY total_ft) AS _35,
            PERCENTILE_CONT(0.4) WITHIN GROUP (ORDER BY total_ft) AS _40,
            PERCENTILE_CONT(0.45) WITHIN GROUP (ORDER BY total_ft) AS _45,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_ft) AS _50,
            PERCENTILE_CONT(0.55) WITHIN GROUP (ORDER BY total_ft) AS _55,
            PERCENTILE_CONT(0.6) WITHIN GROUP (ORDER BY total_ft) AS _60,
            PERCENTILE_CONT(0.65) WITHIN GROUP (ORDER BY total_ft) AS _65,
            PERCENTILE_CONT(0.7) WITHIN GROUP (ORDER BY total_ft) AS _70,
            PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY total_ft) AS _75,
            PERCENTILE_CONT(0.8) WITHIN GROUP (ORDER BY total_ft) AS _80,
            PERCENTILE_CONT(0.85) WITHIN GROUP (ORDER BY total_ft) AS _85,
            PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY total_ft) AS _90,
            PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY total_ft) AS _95,
            PERCENTILE_CONT(1.0) WITHIN GROUP (ORDER BY total_ft) AS _100
        FROM (
            SELECT league_name, 
                CASE WHEN team_home = '{team}' THEN team_home ELSE team_away END AS team, 
                total_ft 
            FROM matches 
            WHERE (team_home = '{team}' OR team_away = '{team}') 
                AND league_name = '{championship}' 
                AND match_date > '{from_date}'
        ) AS team_totals
        GROUP BY league_name, team
        ORDER BY league_name, team;
    """

    # Загрузка данных в DataFrame
    percentiles_df = pd.read_sql_query(sql_query, conn)

    # Закрытие соединения с базой данных
    conn.close()

    return percentiles_df



@app.route('/analysis', methods=['POST','GET'])
def analysis():
    if request.method == 'POST':
        team_home = request.form.get('team_home')
        team_away = request.form.get('team_away')
        championship = request.form.get('championship')
        country = request.form.get('country')
        # Здесь вы должны обрабатывать данные из формы
        # и рендерить шаблон с обновленными данными
    else:
        team_home = request.args.get('team_home')
        team_away = request.args.get('team_away')
        championship = request.args.get('championship')
        country = request.args.get('country')

    from_date = request.form.get('from_date', '2000-01-01') # Default to '2000-01-01' if not provided
    if len(from_date)<1:
        from_date='2000-01-01'
    to_date = str(datetime.today().date()).strip()  # Convert datetime object to string
    print(from_date, to_date)
    print(country,championship,team_home,team_away,'-=-')

    percentiles_df1 = calculate_percentiles(country, championship, team_home, from_date)
    percentiles_df2 = calculate_percentiles(country, championship, team_away, from_date)
    print(percentiles_df1)
    print(percentiles_df2)
    merged_percentiles_df = pd.merge(percentiles_df1, percentiles_df2, on=['league_name', 'team'],
                                     suffixes=('_home', '_away'))

    # Переименовываем столбцы, чтобы отразить команды
    merged_percentiles_df = merged_percentiles_df.rename(columns={'team': 'Team', 'league_name': 'League'})

    # Выводим данные
    print(merged_percentiles_df)
    # print(percentiles_df.to_string())

    if team_home and team_away and championship:
        # Получаем id чемпионата
        championship_id = Championship.query.filter_by(league=championship, country=country).first().id


        # Получаем средние значения total_ft и количество матчей для выбранных команд в выбранном чемпионате
        average_scores_home = db.session.query(func.avg(Match.total_ft)).filter(
            Match.team_home == team_home,
            Match.league_id == championship_id,
            Match.match_date > from_date
        ).scalar()
        print(average_scores_home)
        total_matches_home = db.session.query(func.count()).filter(
            Match.team_home == team_home,
            Match.league_id == championship_id,
            Match.match_date > from_date
        ).scalar()

        team1_total_matches = db.session.query(func.count()).filter(
            (Match.team_home == team_home) | (Match.team_away == team_home),
            Match.league_id == championship_id,
            Match.match_date > from_date
        ).scalar()

        average_scores_away = db.session.query(func.avg(Match.total_ft)).filter(
            Match.team_away == team_away,
            Match.league_id == championship_id,
            Match.match_date > from_date
        ).scalar()

        total_matches_away = db.session.query(func.count()).filter(
            Match.team_away == team_away,
            Match.league_id == championship_id,
            Match.match_date > from_date
        ).scalar()

        team2_total_matches = db.session.query(func.count()).filter(
            (Match.team_home == team_away) | (Match.team_away == team_away),
            Match.league_id == championship_id,
            Match.match_date > from_date
        ).scalar()

        average_scores_home_scored = db.session.query(func.avg(Match.home_score_ft)).filter(
            Match.team_home == team_home,
            Match.league_id == championship_id,
            Match.match_date > from_date
        ).scalar()

        average_scores_home_conceded = db.session.query(func.avg(Match.away_score_ft)).filter(
            Match.team_home == team_home,
            Match.league_id == championship_id,
            Match.match_date > from_date
        ).scalar()

        average_scores_away_scored = db.session.query(func.avg(Match.away_score_ft)).filter(
            Match.team_away == team_away,
            Match.league_id == championship_id,
            Match.match_date > from_date
        ).scalar()

        average_scores_away_conceded = db.session.query(func.avg(Match.home_score_ft)).filter(
            Match.team_away == team_away,
            Match.league_id == championship_id,
            Match.match_date > from_date
        ).scalar()
        try:
            team1_ind_ave_scored_query = db.session.query(func.avg(Match.away_score_ft)).filter(
                Match.team_away == team_home,
                Match.league_id == championship_id,
                Match.match_date > from_date
            ).scalar()
            if team1_ind_ave_scored_query is not None:
                team1_ind_ave_scored = round(
                    (float(team1_ind_ave_scored_query) + float(average_scores_home_scored)) / 2, 1)
            else:
                team1_ind_ave_scored = 0
        except:
            team1_ind_ave_scored = 0

        try:
            team1_ind_ave_conceded_query = db.session.query(func.avg(Match.home_score_ft)).filter(
                Match.team_away == team_home,
                Match.league_id == championship_id,
                Match.match_date > from_date
            ).scalar()
            if team1_ind_ave_conceded_query is not None:
                team1_ind_ave_conceded = round(
                    (float(team1_ind_ave_conceded_query) + float(average_scores_home_conceded)) / 2, 1)
            else:
                team1_ind_ave_conceded = 0
        except:
            team1_ind_ave_conceded = 0

        try:
            team1_anywhere_ave_query = db.session.query(func.avg(Match.total_ft)).filter(
                (Match.team_home == team_home) | (Match.team_away == team_home),
                Match.league_id == championship_id,
                Match.match_date > from_date
            ).scalar()
            if team1_anywhere_ave_query is not None:
                team1_anywhere_ave = team1_anywhere_ave_query
            else:
                team1_anywhere_ave = 0
        except:
            team1_anywhere_ave = 0

        try:
            team2_ind_ave_scored_query = db.session.query(func.avg(Match.home_score_ft)).filter(
                Match.team_home == team_away,
                Match.league_id == championship_id,
                Match.match_date > from_date
            ).scalar()
            if team2_ind_ave_scored_query is not None:
                team2_ind_ave_scored = round(
                    (float(team2_ind_ave_scored_query) + float(average_scores_away_scored)) / 2, 1)
            else:
                team2_ind_ave_scored = 0
        except:
            team2_ind_ave_scored = 0

        try:
            team2_ind_ave_conceded_query = db.session.query(func.avg(Match.away_score_ft)).filter(
                Match.team_home == team_away,
                Match.league_id == championship_id,
                Match.match_date > from_date
            ).scalar()
            if team2_ind_ave_conceded_query is not None:
                team2_ind_ave_conceded = round(
                    (float(team2_ind_ave_conceded_query) + float(average_scores_away_conceded)) / 2, 1)
            else:
                team2_ind_ave_conceded = 0
        except:
            team2_ind_ave_conceded = 0

        try:
            team2_anywhere_ave_query = db.session.query(func.avg(Match.total_ft)).filter(
                (Match.team_home == team_away) | (Match.team_away == team_away),
                Match.league_id == championship_id,
                Match.match_date > from_date
            ).scalar()
            if team2_anywhere_ave_query is not None:
                team2_anywhere_ave = team2_anywhere_ave_query
            else:
                team2_anywhere_ave = 0
        except:
            team2_anywhere_ave = 0

        try:
            average_scores_between_h2h_query = db.session.query(func.avg(Match.total_ft)).filter(
                or_(
                    and_(Match.team_home == team_home, Match.team_away == team_away),
                    and_(Match.team_home == team_away, Match.team_away == team_home)
                ),
                Match.team_home == team_home,
                Match.league_id == championship_id,
                Match.match_date > from_date
            ).scalar()
            if average_scores_between_h2h_query is not None:
                average_scores_between_h2h = average_scores_between_h2h_query
            else:
                average_scores_between_h2h = 0
        except:
            average_scores_between_h2h = 0

        try:
            total_matches_home_between_query = db.session.query(func.count()).filter(
                or_(
                    and_(Match.team_home == team_home, Match.team_away == team_away),
                    and_(Match.team_home == team_away, Match.team_away == team_home)
                ),
                Match.team_home == team_home,
                Match.league_id == championship_id,
                Match.match_date > from_date
            ).scalar()
            if total_matches_home_between_query is not None:
                total_matches_home_between = total_matches_home_between_query
            else:
                total_matches_home_between = 0
        except:
            total_matches_home_between = 0

        try:
            average_scores_home_scored_between_query = db.session.query(func.avg(Match.home_score_ft)).filter(
                or_(
                    and_(Match.team_home == team_home, Match.team_away == team_away),
                    and_(Match.team_home == team_away, Match.team_away == team_home)
                ),
                Match.team_home == team_home,
                Match.league_id == championship_id,
                Match.match_date > from_date
            ).scalar()
            if average_scores_home_scored_between_query is not None:
                average_scores_home_scored_between = average_scores_home_scored_between_query
            else:
                average_scores_home_scored_between = 0
        except:
            average_scores_home_scored_between = 0

        try:
            average_scores_home_conceded_between_query = db.session.query(func.avg(Match.away_score_ft)).filter(
                or_(
                    and_(Match.team_home == team_home, Match.team_away == team_away),
                    and_(Match.team_home == team_away, Match.team_away == team_home)
                ),
                Match.team_home == team_home,
                Match.league_id == championship_id,
                Match.match_date > from_date
            ).scalar()
            if average_scores_home_conceded_between_query is not None:
                average_scores_home_conceded_between = average_scores_home_conceded_between_query
            else:
                average_scores_home_conceded_between = 0
        except:
            average_scores_home_conceded_between = 0

        try:
            team1_ind_ave_scored_between_query = db.session.query(func.avg(Match.away_score_ft)).filter(
                or_(
                    and_(Match.team_home == team_home, Match.team_away == team_away),
                    and_(Match.team_home == team_away, Match.team_away == team_home)
                ),
                Match.team_away == team_home,
                Match.league_id == championship_id,
                Match.match_date > from_date
            ).scalar()
            if team1_ind_ave_scored_between_query is not None:
                team1_ind_ave_scored_between = round(
                    (float(team1_ind_ave_scored_between_query) + float(average_scores_home_scored_between)) / 2, 1)
            else:
                team1_ind_ave_scored_between = 0
        except:
            team1_ind_ave_scored_between = 0

        try:
            team1_ind_ave_conceded_between_query = db.session.query(func.avg(Match.home_score_ft)).filter(
                or_(
                    and_(Match.team_home == team_home, Match.team_away == team_away),
                    and_(Match.team_home == team_away, Match.team_away == team_home)
                ),
                Match.team_away == team_home,
                Match.league_id == championship_id,
                Match.match_date > from_date
            ).scalar()
            if team1_ind_ave_conceded_between_query is not None:
                team1_ind_ave_conceded_between = round(
                    (float(team1_ind_ave_conceded_between_query) + float(average_scores_home_conceded_between)) / 2, 1)
            else:
                team1_ind_ave_conceded_between = 0
        except:
            team1_ind_ave_conceded_between = 0

        all_h2h_matches = len(Match.query.filter(
            or_(
                and_(Match.team_home == team_home, Match.team_away == team_away),
                and_(Match.team_home == team_away, Match.team_away == team_home)
            ),
            Match.match_date > from_date
        ).order_by(desc(Match.match_date)).all())

        return render_template('analysis.html', team_home=team_home, team_away=team_away,
                               country=country, championship=championship,
                               average_scores_home=average_scores_home, total_matches_home=total_matches_home,
                               average_scores_away=average_scores_away, total_matches_away=total_matches_away,
                               average_scores_home_scored=average_scores_home_scored,
                               average_scores_home_conceded=average_scores_home_conceded,
                               average_scores_away_scored=average_scores_away_scored,
                               average_scores_away_conceded=average_scores_away_conceded,
                               team1_ind_ave_scored=team1_ind_ave_scored,team1_ind_ave_conceded=team1_ind_ave_conceded,
                               team1_anywhere_ave=team1_anywhere_ave,
                               team2_ind_ave_scored=team2_ind_ave_scored,team2_ind_ave_conceded=team2_ind_ave_conceded,
                               team2_anywhere_ave=team2_anywhere_ave,
                               team1_total_matches=team1_total_matches,team2_total_matches=team2_total_matches,
                               average_scores_between_h2h=average_scores_between_h2h,
                               total_matches_home_between=total_matches_home_between,
                               average_scores_home_scored_between=average_scores_home_scored_between,
                               average_scores_home_conceded_between=average_scores_home_conceded_between,
                               team1_ind_ave_scored_between=team1_ind_ave_scored_between,
                               team1_ind_ave_conceded_between=team1_ind_ave_conceded_between,
                               all_h2h_matches=all_h2h_matches,
                               merged_percentiles_df=merged_percentiles_df,
                               percentiles_df1=percentiles_df1, percentiles_df2=percentiles_df2)



    else:
        return "Ошибка: Не выбрана команда или чемпионат", 400


if __name__ == '__main__':
    app.run(debug=True)
