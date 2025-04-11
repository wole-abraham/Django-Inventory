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
    i.save()

for i in Accessory.objects.all():
    i.status = 'Good'
    i.return_status = 'Returned'
    i.save()






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
    







