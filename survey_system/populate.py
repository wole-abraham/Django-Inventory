import django
import os
from datetime import datetime
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "survey_system.settings")
django.setup()


# from django.contrib.auth.models import User
# userme = User.objects.filter(username='Mark').first()



from inventory.models import EquipmentsInSurvey, Accessory, EquipmentHistory, AccessoryHistory


for i in EquipmentsInSurvey.objects.all():
    i.status = 'In Store'
    i.chief_surveyor = None
    i.surveyor_responsible = None
    i.save()

import uuid 

for i in Accessory.objects.all():
    uuid_8_digits = str(uuid.uuid4().int)[:8]
    i.serial_number = uuid_8_digits
    i.status = 'Good'
    i.chief_surveyor = None
    i.surveyor_responsible = None
    i.equipment = None
    i.return_status = 'Returned'
    i.save()


ACCESSORY_TYPES = (
        ("tripod", "Tripod"),
        ("levelling_staff", "Levelling Staff"),
        ("tracking_rod", "Tracking Rod"),
        ("reflector", "Reflector"),
        ("gps_extension_bar", "GPS Extension Bar"),
        ("bar_port", "Bar Port"),
        ("powerbank", "Powerbank"),
        ("tribach", "Tribach"),
        ("external_radio_antenna", "External Radio Antenna"),
    )


# for i in ACCESSORY_TYPES:
#     Accessory.objects.create(name=i[0])


# lin = []
# with open('data.csv', 'r') as file:
#      for word in file:
#         pn, name, dateofr, supplier_name, base, roover, data, radio, chief, userr, passs,  pro, section, dateofrec = word.strip().split(',')
#         date_str = dateofr
#         date_str_2 = dateofrec
#         format1, format2 = [datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d"), datetime.strptime(date_str_2, "%d/%m/%Y").strftime("%Y-%m-%d")]

#         EquipmentsInSurvey.objects.create(name=name, date_of_receiving_from_supplier=format1, 
#                                           supplier =supplier_name,
#                                            base_serial=base, 
#                                            roover_serial=roover, 
#                                            data_logger_serial=data, 
#                                            radio_serial = radio,
#                                            chief_surveyor = userme,
                                        
#                                              project = pro,
#                                               section = section,
#                                                date_receiving_from_department = format2
#                                                )
    







