import matplotlib.pyplot as plt
import io

async def create_progress_chart(user_data: dict) -> io.BytesIO:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    
    water_labels = ['Выпито', 'Осталось']
    water_values = [user_data['logged_water'], 
                   max(0, user_data['water_goal'] - user_data['logged_water'])]
    ax1.pie(water_values, labels=water_labels, autopct='%1.1f%%')
    ax1.set_title('Прогресс по воде')
    
    calorie_labels = ['Потреблено', 'Сожжено']
    calorie_values = [user_data['logged_calories'], user_data['burned_calories']]
    ax2.bar(calorie_labels, calorie_values)
    ax2.set_title('Калории')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf