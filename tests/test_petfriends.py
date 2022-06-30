from unittest import result
import pytest
from api import PetFriends
from settings import valid_email, valid_password
import os

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    status, result = pf.get_api_key(email, password)

    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Персик', animal_type='домашний',
                                     age='11', pet_photo='images/persik.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Белка", "кошка", "3", "images/belka.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Персюничек', animal_type='лесной волк', age=10):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


# Тест №1
def test_add_new_pet_simple_with_valid_data_without_photo(name='Белка', animal_type='зайка',
                                                          age='3'):
    """Проверяем возможность добавления нового питомца с корректными данными, но без фото"""

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца без фото
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name
    assert result['pet_photo'] == ''


# Тест №2
def test_add_photo_of_pet(pet_photo='images/belka.jpg'):
    """Проверяем возможность добавления фото в созданного питомца без фото"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Перся", "кофык", "444", "images/persik.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берем первого питомца и добавляем его фото
    status, result = pf.add_photo_of_pet(auth_key, my_pets['pets'][0]['id'], pet_photo)

    # Проверяем, что статус ответа = 200 и у питомца появилось фото
    assert status == 200
    assert result['pet_photo'] != ''


# Тест №3
def test_add_new_pet_with_invalid_pet_photo(name='Персик', animal_type='домашний',
                                            age='11',
                                            pet_photo=' '):
    """Проверяем, что нельзя добавить питомца, если не указан путь до файла с фото"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    try:
        status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    except PermissionError:
        print("Неверный путь к файлу")

# Тест №4
def test_get_api_key_with_invalid_password(email=valid_email, password='123456'):
    """ Проверяем, что при вводе неверного пароля, запрос api ключа не удается, и возвращается статус 403"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403

# Тест №5
def test_add_new_pet_with_valid_data(name='Персик', animal_type='домашний',
                                     age='-1100', pet_photo='images/persik.jpg'):
    """Проверяем, что нельзя добавить питомца с отрицательным возрастом"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 400

# Тест №6
def test_add_new_pet_withot_data_with_photo(name='', animal_type='',
                                     age='', pet_photo='images/persik.jpg'):

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 400

# Тест №7
def test_add_new_pet_with_unacceptable_name(name='!@#$%^&*', animal_type='!@#$%^&*',
                                            age='!@#$%^&*', pet_photo='images/persik.jpg'):
    """Проверяем, что нельзя добавить питомца с символами вместо данных"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 400

# Тест №8
def test_update_self_pet_info_with_invalid_id(name='Belka', animal_type='Lesnaya', age=3):
    """Проверяем отсутствие возможности обновления информации о питомце с неправильным id"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")


    try:
        # Если список не пустой, то пробуем обновить его имя, тип и возраст
        if len(my_pets['pets']) > 0:
            status, result = pf.update_pet_info(auth_key, my_pets['pets'][999]['id'], name, animal_type, age)

        # Проверяем, что появляется сообщение об ошибке
    except IndexError:
        print("Неверный индекс")

# Тест №9
def test_update_pet_info_with_unacceptable_name(name='!@#$%^&*', animal_type='!@#$%^&*', age='!@#$%^&*'):
    """Проверяем отсутствие возможности обновления информации о питомце с неприемлемыми значениями"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

    # Если список пустой, то добавляем питомца и пробуем обновить его имя, тип и возраст
    else:
        pf.add_new_pet(auth_key, "Перся", "кофык", "444", "images/persik.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

    # Проверяем что статус ответа = 400
    assert status == 400

# Тест №10
def test_add_new_pet_with_no_data(name='', animal_type='',
                                  age=''):
    """Проверяем возможность добавления нового питомца без данных"""

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца без фото
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == ''
    assert result['pet_photo'] == ''
