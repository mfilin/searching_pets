import psycopg2

DB_HOST = "HOST NAME"
DB_DATABASE = "DB NAME"
DB_USER = "USER NAME"
DB_PASS = "PASSWORD"
DB_PORT = "PORT"


def create_table():
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_DATABASE, user=DB_USER, password=DB_PASS, port=DB_PORT
    )
    c = conn.cursor()
    c.execute(
        "CREATE TABLE IF NOT EXISTS animals(index SERIAL, description VARCHAR, photo_id VARCHAR, animal_type VARCHAR, gender VARCHAR,\
age VARCHAR, fur VARCHAR, color VARCHAR, character VARCHAR)"
    )
    # c.execute("ALTER TABLE animals ADD COLUMN index SERIAL")
    conn.commit()
    conn.close()


create_table()


def new_admin(id):
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_DATABASE, user=DB_USER, password=DB_PASS, port=DB_PORT
    )
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS admins(id VARCHAR)")
    c.execute("INSERT INTO admins (id) VALUES ('%s')" % (id))
    conn.commit()
    conn.close()


def check_admin(id):
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_DATABASE, user=DB_USER, password=DB_PASS, port=DB_PORT
    )
    c = conn.cursor()
    c.execute("SELECT id FROM admins WHERE id = '%s'" % (id))
    admin = c.fetchall()
    conn.close()
    print(admin)
    if len(admin) != 0:
        return True
    else:
        return False


def delete_admin(id):
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_DATABASE, user=DB_USER, password=DB_PASS, port=DB_PORT
    )
    c = conn.cursor()
    c.execute("DELETE FROM admins WHERE id = %s;" % id)
    conn.commit()
    conn.close()


def new_animal(animal_type, gender, age, fur, color, character, description, photo_id):

    conn = psycopg2.connect(
        host=DB_HOST, database=DB_DATABASE, user=DB_USER, password=DB_PASS, port=DB_PORT
    )
    c = conn.cursor()
    c.execute(
        "INSERT INTO animals (animal_type, gender,age,fur,color,character,description,\
photo_id) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"
        % (animal_type, gender, age, fur, color, character, description, photo_id)
    )
    conn.commit()
    conn.close()


# new_animal('ss','ss','ss','ss','ss','ss','this is a cool cat','jkdghu7r3yetiuhg254uyhguiryg9248')


def find_animal(animal_type, gender, age, fur, color, character):
    """
    age = str(age)
    age = age.replace("'"," ")

    color = str(color)
    color = color.replace("'"," ")

    character = str(character)
    character = character.replace("'", " ")
    """
    gender.append(' ')
    age.append(' ')
    fur.append(' ')
    color.append(' ')
    character.append(' ')

    print(age)
    print(character)
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_DATABASE, user=DB_USER, password=DB_PASS, port=DB_PORT
    )
    c = conn.cursor()
    c.execute(
        f"""SELECT (description) FROM animals WHERE animal_type = '{animal_type}' 
AND gender in {tuple(gender)} AND age in {tuple(age)} AND fur in {tuple(fur)} AND color in {tuple(color)} 
AND character in {tuple(character)} """
    )
    description = c.fetchall()

    c.execute(
        f"""SELECT (photo_id) FROM animals WHERE animal_type = '{animal_type}' 
AND gender in {tuple(gender)} AND age in {tuple(age)} AND fur in {tuple(fur)} AND color in {tuple(color)} 
AND character in {tuple(character)} """
    )
    photo_id = c.fetchall()
    conn.close()

    output = []
    
    for i in range(len(photo_id)):
        output.append((description[i][0],photo_id[i][0]))
    return output


def get_all_animals():

    conn = psycopg2.connect(
        host=DB_HOST, database=DB_DATABASE, user=DB_USER, password=DB_PASS, port=DB_PORT
    )
    c = conn.cursor()
    c.execute("SELECT * FROM animals")
    animal_list = c.fetchall()
    conn.close()
    return animal_list


# print('found animal is = ' + str(find_animal('ss','ss','ss','ss','ss','ss')))
print(get_all_animals())


def delete_animal(index):
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_DATABASE, user=DB_USER, password=DB_PASS, port=DB_PORT
    )
    c = conn.cursor()
    c.execute("DELETE FROM animals WHERE index = %s;" % index)
    conn.commit()
    conn.close()


"""
print( 'Вот что нашлось : ' + str(
find_animal ('Кошка', 'Женский', ['1-3 Года', 'Старше 7 лет'], 'Длинная/пушистая', 
['Тигровый', 'Черепаховый'], ['Независимый']))
)
"""

print( 'Вот что нашлось : ' + str(
find_animal ('Кошка', ['Мужской'], ['3-7 Лет'], ['Длинная/пушистая'], 
['Черно-белый'], ['Дружелюбный', 'ksajdhfks'])))

