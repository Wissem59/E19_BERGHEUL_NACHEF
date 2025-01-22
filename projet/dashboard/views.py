from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Max, Count
from datetime import datetime, timedelta
from app.models import Personnel
from salaire.models import Presence
from recrutement.models import Offre_emploi, Candidature
from django.utils.timezone import now
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import matplotlib

# Use the Agg backend for rendering charts
matplotlib.use('Agg')

# Helper functions
def improve_chart_style():
    """Apply a consistent style to all charts."""
    plt.style.use('ggplot')

def save_chart_as_base64():
    """Save the current matplotlib chart as a base64-encoded string."""
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    chart_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    return chart_base64

# Generate pastel colors dynamically based on the number of sections in a pie chart
def generate_pastel_colors(num_colors):
    pastel_colors = [
        '#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFB3', '#BAFFFF', '#B3D9FF', '#C1B3FF', '#FFB3FF'
    ]  # List of pastel colors in hex format
    return pastel_colors[:num_colors]

def generate_chart(title, x_data, y_data, chart_type='line', colors=None, x_label='', y_label=''):
    """Generate a chart with the specified parameters, excluding zero values from labels."""
    improve_chart_style()
    plt.figure(figsize=(10, 6))

    if chart_type == 'line':
        plt.plot(x_data, y_data, marker='o', linestyle='-', color=colors or '#4c8a8a', markersize=8, linewidth=2)
    elif chart_type == 'bar':
        plt.bar(x_data, y_data, color=colors or '#5b7f6d', edgecolor='black', linewidth=1.2)
    elif chart_type == 'pie':
        # Remove zero values from the data and labels
        non_zero_x_data = [x for x, y in zip(x_data, y_data) if y != 0]
        non_zero_y_data = [y for y in y_data if y != 0]
        
        # Generate pastel colors based on the remaining non-zero data
        pastel_colors = generate_pastel_colors(len(non_zero_x_data))
        
        # Create the pie chart without zero values
        wedges, texts, autotexts = plt.pie(
            non_zero_y_data, labels=non_zero_x_data, autopct='%1.1f%%', colors=pastel_colors, startangle=90, shadow=True
            )
        
        # Add a legend for the pie chart
        plt.legend(wedges, non_zero_x_data, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    plt.title(title, fontsize=16, fontweight='bold')
    plt.xlabel(x_label, fontsize=12)
    plt.ylabel(y_label, fontsize=12)
    plt.grid(True, linestyle='--', linewidth=0.5)

    return save_chart_as_base64()

def filter_absences(records, time_frame):
    data = {}
    current_date = datetime.now()

    if time_frame == 'week':
        # Group absences by day of the week (Sunday, Monday, etc.)
        start_of_week = current_date - timedelta(days=current_date.weekday())  # Monday
        days_of_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        for i, day_name in enumerate(days_of_week):
            day_start = start_of_week + timedelta(days=i)
            day_end = day_start + timedelta(days=1) - timedelta(seconds=1)
            day_count = records.filter(date_absence__range=(day_start, day_end)).count()
            data[day_name] = day_count

    elif time_frame == 'month':
        # Group absences by week of the month
        start_of_month = current_date.replace(day=1)
        weeks_of_month = []
        for week_num in range(0, 5):  # Up to 5 weeks in a month
            week_name = f"Week {week_num + 1}"
            week_start = start_of_month + timedelta(weeks=week_num)
            week_end = week_start + timedelta(weeks=1) - timedelta(seconds=1)
            week_count = records.filter(date_absence__range=(week_start, week_end)).count()
            weeks_of_month.append(week_name)  # "Week 1", "Week 2", etc.
            data[week_name] = week_count  # Ensure this is a list, not nested lists

    elif time_frame == 'year':
        # Group absences by month of the year
        start_of_year = current_date.replace(month=1, day=1)
        months_of_year = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
        for month_num, month_name in zip(range(1, 13), months_of_year):
            month_start = start_of_year.replace(month=month_num, day=1)
            month_end = (month_start + timedelta(days=31)).replace(day=1) - timedelta(seconds=1)
            month_count = records.filter(date_absence__range=(month_start, month_end)).count()
            data[month_name] = month_count

    elif time_frame == 'five_years':
        # Group absences by year for the last 5 years
        start_of_five_years = current_date.replace(year=current_date.year - 5, month=1, day=1)
        for year in range(start_of_five_years.year, current_date.year + 1):
            year_start = datetime(year, 1, 1)
            year_end = datetime(year, 12, 31, 23, 59, 59)
            year_count = records.filter(date_absence__range=(year_start, year_end)).count()
            data[year] = year_count

    return list(data.keys()), list(data.values())

def absence_peaks_view(time_frame, presence_records):
    absence_dates, absence_counts = filter_absences(presence_records, time_frame)

    chart_title = f"Absence Peaks ({time_frame.capitalize()})"
    chart = generate_chart(chart_title, absence_dates, absence_counts, chart_type='bar', x_label='Time', y_label='Absences')
    
    return absence_dates, absence_counts, chart

# Views
def contract_type_distribution_view():
    """Generate the contract type distribution chart."""
    contract_types = ['CDI', 'CDD', 'STAGE', 'AUTRE']
    counts = [
        Personnel.objects.filter(contrats__type_contrat__iexact='CDI', contrats__archive=False).count(),
        Personnel.objects.filter(contrats__type_contrat__iexact='CDD', contrats__archive=False).count(),
        Personnel.objects.filter(contrats__type_contrat__iexact='STAGE', contrats__archive=False).count(),
        Personnel.objects.filter(contrats__type_contrat__iexact='AUTRE', contrats__archive=False).count(),
    ]
    chart = generate_chart('Contract Type Distribution', contract_types, counts, chart_type='pie')
    return chart

def diversity_view():
    """Calculate and generate the diversity chart."""
    diversity = {
        'male': Personnel.objects.filter(gender='M').count(),
        'female': Personnel.objects.filter(gender='F').count(),
    }
    chart = generate_chart('Diversity (Gender)', ['Male', 'Female'], [diversity['male'], diversity['female']], chart_type='pie')
    return diversity, chart

from datetime import datetime

def age_distribution_view():
    """Calculate and generate the age distribution chart."""
    age_ranges = {'20-30': 0, '30-40': 0, '40+': 0}
    today = datetime.now().date()

    for personnel in Personnel.objects.all():
        if personnel.date_naissance:  # Check if date_naissance is not None
            age = (today - personnel.date_naissance).days // 365
            if 20 <= age <= 30:
                age_ranges['20-30'] += 1
            elif 30 < age <= 40:
                age_ranges['30-40'] += 1
            elif age > 40:
                age_ranges['40+'] += 1
        else:
            # Optionally, log or handle cases where date_naissance is None
            print(f"Warning: Personnel {personnel} has no date_naissance set.")

    chart = generate_chart('Age Distribution', list(age_ranges.keys()), list(age_ranges.values()), chart_type='bar')
    return age_ranges, chart


def gender_distribution_view():
    """Generate a gender distribution chart."""
    gender_data = {
        'Male': Personnel.objects.filter(gender='M').count(),
        'Female': Personnel.objects.filter(gender='F').count(),
    }
    chart = generate_chart('Gender Distribution', list(gender_data.keys()), list(gender_data.values()), chart_type='pie')
    return gender_data, chart

def top_performers_view():
    """Retrieve the top five performers, excluding those with no evaluation scores."""
    top_performers = (
        Personnel.objects.annotate(
            max_performance_rating=Max('evaluations__performance_rating')
        )
        .filter(max_performance_rating__isnull=False)  # Exclude personnel with no scores
        .order_by('-max_performance_rating')[:5]      # Take the top 5 based on scores
    )

    return top_performers

def salary_distribution_view():
    """Calculate average and median salary with distribution chart."""
    salaries = Personnel.objects.values_list('salaire', flat=True)
    # Ensure there are no None values in the salaries list
    salaries = [salary for salary in salaries if salary is not None]
    
    # Calculate the average salary safely
    avg_salary = sum(salaries) / len(salaries) if salaries else 0
    median_salary = sorted(salaries)[len(salaries) // 2] if salaries else 0
    salary_ranges = {'<2000': 0, '2000-4000': 0, '>4000': 0}
    for salary in salaries:
        if salary < 2000:
            salary_ranges['<2000'] += 1
        elif 2000 <= salary <= 4000:
            salary_ranges['2000-4000'] += 1
        else:
            salary_ranges['>4000'] += 1
    chart = generate_chart('Salary Distribution', list(salary_ranges.keys()), list(salary_ranges.values()), chart_type='bar')
    return {'avg_salary': avg_salary, 'median_salary': median_salary}, chart

def generate_tenure_chart():
    """Generate a chart for tenure distribution."""
    tenure_ranges = {'<1 year': 0, '1-3 years': 0, '3+ years': 0}
    
    # Calculate tenure for each employee
    for personnel in Personnel.objects.all():
        tenure_years = (datetime.now().date() - personnel.hireDate).days // 365
        if tenure_years < 1:
            tenure_ranges['<1 year'] += 1
        elif 1 <= tenure_years <= 3:
            tenure_ranges['1-3 years'] += 1
        else:
            tenure_ranges['3+ years'] += 1
    
    chart = generate_chart('Tenure Distribution', list(tenure_ranges.keys()), list(tenure_ranges.values()), chart_type='bar')
    return chart

def filter_candidatures(records, time_frame):
    """Filter and group candidatures based on the selected timeframe."""
    data = {}
    current_date = now()

    if time_frame == 'week':
        start_of_week = current_date - timedelta(days=current_date.weekday())  # Monday
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for i, day_name in enumerate(days_of_week):
            day_start = start_of_week + timedelta(days=i)
            day_end = day_start + timedelta(days=1) - timedelta(seconds=1)
            day_count = records.filter(date_candidature__range=(day_start, day_end)).count()
            data[day_name] = day_count

    elif time_frame == 'month':
        start_of_month = current_date.replace(day=1)
        while start_of_month.month == current_date.month:
            week_name = f"Week {len(data) + 1}"
            week_end = start_of_month + timedelta(days=6)
            week_count = records.filter(date_candidature__range=(start_of_month, week_end)).count()
            data[week_name] = week_count
            start_of_month += timedelta(days=7)

    elif time_frame == 'year':
        start_of_year = current_date.replace(month=1, day=1)
        for month_num in range(1, 13):
            month_start = start_of_year.replace(month=month_num)
            next_month = month_start.replace(month=month_num + 1) if month_num < 12 else start_of_year.replace(year=current_date.year + 1, month=1)
            month_end = next_month - timedelta(seconds=1)
            month_count = records.filter(date_candidature__range=(month_start, month_end)).count()
            data[month_start.strftime('%B')] = month_count

    return list(data.keys()), list(data.values())

def candidature_status_view(time_frame):
    """Generate candidature status statistics and chart based on the selected timeframe."""
    records = Candidature.objects.all()
    dates, counts = filter_candidatures(records, time_frame)

    statuses = ['En attente', 'Accepté', 'Rejeté']
    status_counts = [
        records.filter(statut_candidature='En attente').count(),
        records.filter(statut_candidature='Accepté').count(),
        records.filter(statut_candidature='Rejeté').count(),
    ]

    chart = generate_chart(
        f'Candidature Status Distribution ({time_frame.capitalize()})',
        statuses,
        status_counts,
        chart_type='pie',
    )

    return {'dates': dates, 'counts': counts, 'status_counts': status_counts, 'chart': chart}

def offres_postees_view():
    """Generate statistics for how many job offers were posted."""
    current_year = datetime.now().year 
    offers_posted_data = Offre_emploi.objects.filter(date_publication__year=current_year).values('date_publication__month').annotate(count=Count('id_offre'))
    offer_months = [datetime(current_year, data['date_publication__month'], 1).strftime('%b') for data in offers_posted_data]
    offer_counts = [data['count'] for data in offers_posted_data]
    chart = generate_chart('Offres d\'Emploi Postées', offer_months, offer_counts, chart_type='bar')
    return offer_months, offer_counts, chart

@login_required
def dashboard(request):
    """Main dashboard view to aggregate all data."""
    total_personnels_count = Personnel.objects.count()

    # Contract statistics
    contract_stats = {
        'cdi': Personnel.objects.filter(contrats__type_contrat__iexact='CDI', contrats__archive=False).count(),
        'cdd': Personnel.objects.filter(contrats__type_contrat__iexact='CDD', contrats__archive=False).count(),
        'stage': Personnel.objects.filter(contrats__type_contrat__iexact='STAGE', contrats__archive=False).count(),
        'autre': Personnel.objects.filter(contrats__type_contrat__iexact='AUTRE', contrats__archive=False).count(),
    }

    # Generate contract type distribution chart
    contract_type_chart = contract_type_distribution_view()

    # Diversity data
    diversity, diversity_chart = diversity_view()

    # Gender distribution chart
    gender_data, gender_chart = gender_distribution_view()

    # Age distribution
    age_ranges, age_distribution_chart = age_distribution_view()

    # Tenure distribution
    tenure_chart = generate_tenure_chart()

    # Top performers
    top_performers = top_performers_view()

    # Absence peaks
    time_frame = request.GET.get('time_frame', 'week')
    presence_records = Presence.objects.all()
    absence_dates, absence_counts, absence_peaks_chart = absence_peaks_view(time_frame, presence_records)

    # Salary distribution
    salary_stats, salary_distribution_chart = salary_distribution_view()

    # Candidature stats
    candidature_time_frame = request.GET.get('candidature_time_frame', 'week')
    candidature_dates, candidature_counts = filter_candidatures(Candidature.objects.all(), candidature_time_frame)
    candidature_total = sum(candidature_counts) 
    candidature_status_chart = candidature_status_view(candidature_time_frame)['chart']

    # Context for the template
    context = {
        'info': {'total_employees': total_personnels_count},
        'contract_stats': contract_stats,
        'contract_type_chart': contract_type_chart,
        'diversity': diversity,
        'diversity_chart': diversity_chart,
        'gender_chart': gender_chart,
        'age_distribution_chart': age_distribution_chart,
        'tenure_distribution_chart': tenure_chart,
        'absence_analysis': {
            'peak_period': absence_dates[absence_counts.index(max(absence_counts))] if absence_counts else 'N/A',
            'average_days': round(sum(absence_counts) / len(absence_counts)) if absence_counts else 0,
        },
        'absence_chart': absence_peaks_chart,
        'salary_stats': salary_stats,
        'salary_distribution_chart': salary_distribution_chart,
        'top_performers': top_performers,
        'candidature_status_chart': candidature_status_chart,
        'candidature_stats': {
            'dates': candidature_dates,
            'counts': candidature_counts,
            'candidature_count': candidature_total,
        },
        'current_url': request.path.lstrip('/'),
    }

    return render(request, 'dashboard/dashboard.html', context)
    