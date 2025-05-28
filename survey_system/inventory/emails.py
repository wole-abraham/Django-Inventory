import requests


def returning_equipment_email(subject, instance):
    equipment = instance
    accessories = equipment.accessories.all()

    accessory_items = ""
    if accessories:
        for acc in accessories:
            accessory_items += f"<li>{acc.name.capitalize()} - {acc.status}</li>"
    else:
        accessory_items = "<li>No accessories recorded.</li>"
    
    message = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Equipment Returning Notification</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      background-color: #f4f6f8;
      padding: 20px;
    }}
    .container {{
      background-color: #ffffff;
      padding: 25px;
      border-radius: 6px;
      max-width: 600px;
      margin: auto;
      box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }}
    h2 {{
      color: #2d3748;
      margin-bottom: 10px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
    }}
    td {{
      padding: 6px 0;
      vertical-align: top;
    }}
    .label {{
      color: #718096;
      font-weight: bold;
      width: 160px;
    }}
    .value {{
      color: #2d3748;
    }}
    ul {{
      padding-left: 18px;
      margin: 0;
    }}
    li {{
      margin-bottom: 5px;
    }}
    .footer {{
      margin-top: 30px;
      font-size: 13px;
      color: #a0aec0;
      text-align: center;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h2>📩 Equipment Returning</h2>

    <p>The following equipment is returning to the store:</p>

    <table>
      <tr>
        <td class="label">Status:</td>
        <td class="value">{equipment.status}</td>
      </tr>
      <tr>
        <td class="label">Surveyor:</td>
        <td class="value">{equipment.chief_surveyor}</td>
      </tr>
      <tr>
        <td class="label">Equipment Name:</td>
        <td class="value">{equipment.name}</td>
      </tr>
      <tr>
        <td class="label">Base Serial:</td>
        <td class="value">{equipment.base_serial}</td>
      </tr>
      <tr>
        <td class="label">Section:</td>
        <td class="value">{equipment.section}</td>
      </tr>
      <tr>
        <td class="label">Project:</td>
        <td class="value">{equipment.project}</td>
      </tr>
      <tr>
        <td class="label">Accessories:</td>
        <td class="value">
          <ul>
            {accessory_items}
          </ul>
        </td>
      </tr>
    </table>

    <div class="footer">
      Equipment Management System Notification • Do not reply to this message.
    </div>
  </div>
</body>
</html>
"""
    return message



def returned_equipment_email(subject, instance):
    equipment = instance
    accessories = equipment.accessories.all()

    accessory_items = ""
    if accessories:
        for acc in accessories:
            accessory_items += f"<li>{acc.name.capitalize()} - {acc.status}</li>"
    else:
        accessory_items = "<li>No accessories recorded.</li>"
    
    message = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Equipment Returned Notification</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      background-color: #f4f6f8;
      padding: 20px;
    }}
    .container {{
      background-color: #ffffff;
      padding: 25px;
      border-radius: 6px;
      max-width: 600px;
      margin: auto;
      box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }}
    h2 {{
      color: #2d3748;
      margin-bottom: 10px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
    }}
    td {{
      padding: 6px 0;
      vertical-align: top;
    }}
    .label {{
      color: #718096;
      font-weight: bold;
      width: 160px;
    }}
    .value {{
      color: #2d3748;
    }}
    ul {{
      padding-left: 18px;
      margin: 0;
    }}
    li {{
      margin-bottom: 5px;
    }}
    .footer {{
      margin-top: 30px;
      font-size: 13px;
      color: #a0aec0;
      text-align: center;
    }}
  </style>
</head>
<body>
  <div class="container">
     <h2>✅ Equipment Returned</h2>

    <p>The following equipment is returning to the store:</p>

    <table>
      <tr>
        <td class="label">Status:</td>
        <td class="value">{equipment.status}</td>
      </tr>
      <tr>
        <td class="label">Surveyor:</td>
        <td class="value">{equipment.chief_surveyor}</td>
      </tr>
      <tr>
        <td class="label">Equipment Name:</td>
        <td class="value">{equipment.name}</td>
      </tr>
      <tr>
        <td class="label">Base Serial:</td>
        <td class="value">{equipment.base_serial}</td>
      </tr>
      <tr>
        <td class="label">Section:</td>
        <td class="value">{equipment.section}</td>
      </tr>
      <tr>
        <td class="label">Project:</td>
        <td class="value">{equipment.project}</td>
      </tr>
      <tr>
        <td class="label">Accessories:</td>
        <td class="value">
          <ul>
            {accessory_items}
          </ul>
        </td>
      </tr>
    </table>

    <div class="footer">
      Equipment Management System Notification • Do not reply to this message.
    </div>
  </div>
</body>
</html>
"""
    return message




def released_equipment_email(subject, instance):
    equipment = instance
    accessories = equipment.accessories.all()

    accessory_items = ""
    if accessories:
        for acc in accessories:
            accessory_items += f"<li>{acc.name.capitalize()} - {acc.status}</li>"
    else:
        accessory_items = "<li>No accessories recorded.</li>"
    
    message = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Equipment Release Notification</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      background-color: #f4f6f8;
      padding: 20px;
    }}
    .container {{
      background-color: #ffffff;
      padding: 25px;
      border-radius: 6px;
      max-width: 600px;
      margin: auto;
      box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }}
    h2 {{
      color: #2d3748;
      margin-bottom: 10px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
    }}
    td {{
      padding: 6px 0;
      vertical-align: top;
    }}
    .label {{
      color: #718096;
      font-weight: bold;
      width: 160px;
    }}
    .value {{
      color: #2d3748;
    }}
    ul {{
      padding-left: 18px;
      margin: 0;
    }}
    li {{
      margin-bottom: 5px;
    }}
    .footer {{
      margin-top: 30px;
      font-size: 13px;
      color: #a0aec0;
      text-align: center;
    }}
  </style>
</head>
<body>
  <div class="container">
       <h2>📤 Equipment Released</h2>

    <p>The following equipment is has been release to the surveyor {equipment.chief_surveyor}:</p>

    <table>
      <tr>
        <td class="label">Status:</td>
        <td class="value">{equipment.status}</td>
      </tr>
      <tr>
        <td class="label">Surveyor:</td>
        <td class="value">{equipment.chief_surveyor}</td>
      </tr>
      <tr>
        <td class="label">Equipment Name:</td>
        <td class="value">{equipment.name}</td>
      </tr>
      <tr>
        <td class="label">Base Serial:</td>
        <td class="value">{equipment.base_serial}</td>
      </tr>
      <tr>
        <td class="label">Section:</td>
        <td class="value">{equipment.section}</td>
      </tr>
      <tr>
        <td class="label">Project:</td>
        <td class="value">{equipment.project}</td>
      </tr>
      <tr>
        <td class="label">Accessories:</td>
        <td class="value">
          <ul>
            {accessory_items}
          </ul>
        </td>
      </tr>
    </table>

    <div class="footer">
      Equipment Management System Notification • Do not reply to this message.
    </div>
  </div>
</body>
</html>
"""
    return message




def released_equipment_field_email(subject, instance):
    equipment = instance
    accessories = equipment.accessories.all()

    accessory_items = ""
    if accessories:
        for acc in accessories:
            accessory_items += f"<li>{acc.name.capitalize()} - {acc.status}</li>"
    else:
        accessory_items = "<li>No accessories recorded.</li>"
    
    message = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Equipment In Field  Notification</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      background-color: #f4f6f8;
      padding: 20px;
    }}
    .container {{
      background-color: #ffffff;
      padding: 25px;
      border-radius: 6px;
      max-width: 600px;
      margin: auto;
      box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }}
    h2 {{
      color: #2d3748;
      margin-bottom: 10px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
    }}
    td {{
      padding: 6px 0;
      vertical-align: top;
    }}
    .label {{
      color: #718096;
      font-weight: bold;
      width: 160px;
    }}
    .value {{
      color: #2d3748;
    }}
    ul {{
      padding-left: 18px;
      margin: 0;
    }}
    li {{
      margin-bottom: 5px;
    }}
    .footer {{
      margin-top: 30px;
      font-size: 13px;
      color: #a0aec0;
      text-align: center;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h2>📩 Equipment In Field</h2>

    <p>The following equipment is has been released to the Field by  {equipment.chief_surveyor}:</p>

    <table>
      <tr>
        <td class="label">Status:</td>
        <td class="value">{equipment.status}</td>
      </tr>
      <tr>
        <td class="label">Surveyor:</td>
        <td class="value">{equipment.chief_surveyor}</td>
      </tr>
      <tr>
        <td class="label">Equipment Name:</td>
        <td class="value">{equipment.name}</td>
      </tr>
      <tr>
        <td class="label">Base Serial:</td>
        <td class="value">{equipment.base_serial}</td>
      </tr>
      <tr>
        <td class="label">Section:</td>
        <td class="value">{equipment.section}</td>
      </tr>
      <tr>
        <td class="label">Project:</td>
        <td class="value">{equipment.project}</td>
      </tr>
      <tr>
        <td class="label">Surveyor Responsible:</td>
        <td class="value">{equipment.surveyor_responsible}</td>
      </tr>
      <tr>
        <td class="label">Accessories:</td>
        <td class="value">
          <ul>
            {accessory_items}
          </ul>
        </td>
      </tr>
    </table>

    <div class="footer">
      Equipment Management System Notification • Do not reply to this message.
    </div>
  </div>
</body>
</html>
"""
    return message




def delivery_email(subject, instance):
    equipment = instance
    accessories = equipment.accessories.all()

    accessory_items = ""
    if accessories:
        for acc in accessories:
            accessory_items += f"<li>{acc.name.capitalize()} - {acc.status}</li>"
    else:
        accessory_items = "<li>No accessories recorded.</li>"
    
    message = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Equipment In Field  Notification</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      background-color: #f4f6f8;
      padding: 20px;
    }}
    .container {{
      background-color: #ffffff;
      padding: 25px;
      border-radius: 6px;
      max-width: 600px;
      margin: auto;
      box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }}
    h2 {{
      color: #2d3748;
      margin-bottom: 10px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
    }}
    td {{
      padding: 6px 0;
      vertical-align: top;
    }}
    .label {{
      color: #718096;
      font-weight: bold;
      width: 160px;
    }}
    .value {{
      color: #2d3748;
    }}
    ul {{
      padding-left: 18px;
      margin: 0;
    }}
    li {{
      margin-bottom: 5px;
    }}
    .footer {{
      margin-top: 30px;
      font-size: 13px;
      color: #a0aec0;
      text-align: center;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h2>📩 Equipment Is Being Delivered</h2>

    <p>The following equipment is Being Delivered To:  {equipment.chief_surveyor}:</p>

    <table>
      <tr>
        <td class="label">Status:</td>
        <td class="value">{equipment.status}</td>
      </tr>
      <tr>
        <td class="label">Surveyor:</td>
        <td class="value">{equipment.chief_surveyor}</td>
      </tr>
      <tr>
        <td class="label">Equipment Name:</td>
        <td class="value">{equipment.name}</td>
      </tr>
      <tr>
        <td class="label">Base Serial:</td>
        <td class="value">{equipment.base_serial}</td>
      </tr>
      <tr>
        <td class="label">Section:</td>
        <td class="value">{equipment.section}</td>
      </tr>
      <tr>
        <td class="label">Project:</td>
        <td class="value">{equipment.project}</td>
      </tr>
      <tr>
        <td class="label">Surveyor Responsible:</td>
        <td class="value">{equipment.surveyor_responsible}</td>
      </tr>
      <tr>
        <td class="label">Accessories:</td>
        <td class="value">
          <ul>
            {accessory_items}
          </ul>
        </td>
      </tr>
    </table>

    <div class="footer">
      Equipment Management System Notification • Do not reply to this message.
    </div>
  </div>
</body>
</html>
"""
    return message




def delivery_cancelled(subject, instance):
    equipment = instance
    accessories = equipment.accessories.all()

    accessory_items = ""
    if accessories:
        for acc in accessories:
            accessory_items += f"<li>{acc.name.capitalize()} - {acc.status}</li>"
    else:
        accessory_items = "<li>No accessories recorded.</li>"
    
    message = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Delivery Cancelled</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      background-color: #f4f6f8;
      padding: 20px;
    }}
    .container {{
      background-color: #ffffff;
      padding: 25px;
      border-radius: 6px;
      max-width: 600px;
      margin: auto;
      box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }}
    h2 {{
      color: #2d3748;
      margin-bottom: 10px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
    }}
    td {{
      padding: 6px 0;
      vertical-align: top;
    }}
    .label {{
      color: #718096;
      font-weight: bold;
      width: 160px;
    }}
    .value {{
      color: #2d3748;
    }}
    ul {{
      padding-left: 18px;
      margin: 0;
    }}
    li {{
      margin-bottom: 5px;
    }}
    .footer {{
      margin-top: 30px;
      font-size: 13px;
      color: #a0aec0;
      text-align: center;
    }}
  </style>
</head>
<body>
  <div class="container">
     <h2>❌ Delivery Cancelled</h2>

    <p>The following equipment has been Cancelled for Delivery  {equipment.chief_surveyor}:</p>

    <table>
      <tr>
        <td class="label">Status:</td>
        <td class="value">{equipment.status}</td>
      </tr>
      <tr>
        <td class="label">Surveyor:</td>
        <td class="value">{equipment.chief_surveyor}</td>
      </tr>
      <tr>
        <td class="label">Equipment Name:</td>
        <td class="value">{equipment.name}</td>
      </tr>
      <tr>
        <td class="label">Base Serial:</td>
        <td class="value">{equipment.base_serial}</td>
      </tr>
      <tr>
        <td class="label">Section:</td>
        <td class="value">{equipment.section}</td>
      </tr>
      <tr>
        <td class="label">Project:</td>
        <td class="value">{equipment.project}</td>
      </tr>
      <tr>
        <td class="label">Surveyor Responsible:</td>
        <td class="value">{equipment.surveyor_responsible}</td>
      </tr>
      <tr>
        <td class="label">Accessories:</td>
        <td class="value">
          <ul>
            {accessory_items}
          </ul>
        </td>
      </tr>
    </table>

    <div class="footer">
      Equipment Management System Notification • Do not reply to this message.
    </div>
  </div>
</body>
</html>
"""
    return message




def received_equipment(subject, instance):
  equipment = instance
  accessories = equipment.accessories.all()

  accessory_items = ""
  if accessories:
    for acc in accessories:
      accessory_items += f"<li>{acc.name.capitalize()} - {acc.status}</li>"
  else:
    accessory_items = "<li>No accessories recorded.</li>"
  
  message = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Equipment Received Notification</title>
  <style>
  body {{
    font-family: Arial, sans-serif;
    background-color: #f4f6f8;
    padding: 20px;
  }}
  .container {{
    background-color: #ffffff;
    padding: 25px;
    border-radius: 6px;
    max-width: 600px;
    margin: auto;
    box-shadow: 0 0 10px rgba(0,0,0,0.05);
  }}
  h2 {{
    color: #2d3748;
    margin-bottom: 10px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
  }}
  td {{
    padding: 6px 0;
    vertical-align: top;
  }}
  .label {{
    color: #718096;
    font-weight: bold;
    width: 160px;
  }}
  .value {{
    color: #2d3748;
  }}
  ul {{
    padding-left: 18px;
    margin: 0;
  }}
  li {{
    margin-bottom: 5px;
  }}
  .footer {{
    margin-top: 30px;
    font-size: 13px;
    color: #a0aec0;
    text-align: center;
  }}
  </style>
</head>
<body>
  <div class="container">
   <h2>📥 Equipment Received</h2>

  <p>The following equipment has been received by {equipment.chief_surveyor}:</p>

  <table>
    <tr>
    <td class="label">Status:</td>
    <td class="value">{equipment.status}</td>
    </tr>
    <tr>
    <td class="label">Surveyor:</td>
    <td class="value">{equipment.chief_surveyor}</td>
    </tr>
    <tr>
    <td class="label">Equipment Name:</td>
    <td class="value">{equipment.name}</td>
    </tr>
    <tr>
    <td class="label">Base Serial:</td>
    <td class="value">{equipment.base_serial}</td>
    </tr>
    <tr>
    <td class="label">Section:</td>
    <td class="value">{equipment.section}</td>
    </tr>
    <tr>
    <td class="label">Project:</td>
    <td class="value">{equipment.project}</td>
    </tr>
    <tr>
    <td class="label">Surveyor Responsible:</td>
    <td class="value">{equipment.surveyor_responsible}</td>
    </tr>
    <tr>
    <td class="label">Accessories:</td>
    <td class="value">
      <ul>
      {accessory_items}
      </ul>
    </td>
    </tr>
  </table>

  <div class="footer">
    Equipment Management System Notification • Do not reply to this message.
  </div>
  </div>
</body>
</html>
"""
  return message
