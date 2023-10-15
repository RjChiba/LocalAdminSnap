from typing import Union
from datetime import datetime
import random


class UserID():
    def __init__(self):
        self.hist = set()

    def gen(self):
        while True:
            candID = random.randrange(111111111,999999999)
            if candID not in self.hist:
                self.hist.add(candID)
                return candID

userID = UserID()

snap = []

class AdminDivision:
    def __init__(self, name: str, parent_division: Union['AdminDivision', None] = None):
        self.name = name
        self.ID = userID.gen()
        self.parent = parent_division
        self.location = parent_division.location + [self.ID] if parent_division != None else [self.ID]
        self.children = []
        self.depth = 0 if parent_division == None else parent_division.depth + 1
        self.status = "Active"

    def __str__(self):
        return f"""{'='*20}
name      : {self.name}
ID        : {self.ID}
parent    : {self.parent.name if self.parent != None else None}
location  : {"/".join(list(map(str, self.location)))}
children  : {", ".join([ c.name for c in self.children] )}
depth     : {self.depth}
stats     : {self.status}
"""

class AdminChange:
    def __init__(self, date: datetime, description: Union[str, None] = None):
        self.date = date
        self.ID = userID.gen()
        self.description = description

    def log(self):
        snap.append(self)

class newAdminChange(AdminChange):
    def __init__(self, date: datetime, name: str, parent_division: Union['AdminDivision', None] = None, description: Union[str, None] = None):
        super().__init__(date, description)
        self.AD = AdminDivision(name, parent_division)
        if parent_division != None:
            parent_division.children.append(self.AD)

        super().log()

    def export(self):
        return self.AD

    def __str__(self):
        return f"""
* newAdminChange {self.ID}
  Date: {self.date}
    {self.AD.parent.name if self.AD.depth != 0 else None} > *{self.AD.name}*
    {"/".join(map(str, self.AD.location))}
    {self.description}
"""

class deactivateAdminChange(AdminChange):
    def __init__(self, date: datetime, admin: AdminDivision, description: Union[str, None] = None):
        super().__init__(date, description)
        admin.status = "Deactivate"
        self.AD = admin

        super().log()

    def __str__(self):
        return f"""
* deactivateAdminChange {self.ID}
  Date: {self.date}
    {self.AD.name}
    {self.description}
"""

class nameAdminChange(AdminChange):
    def __init__(self, date: datetime, admin: AdminDivision, newname: str, description: Union[str, None] = None):
        super().__init__(date, description)
        self.oldname = admin.name 
        self.newname = newname
        admin.name = newname
        self.AD = admin

        super().log()

    def __str__(self):
        return f"""
* nameAdminChange {self.ID}
  Date: {self.date}
    {self.oldname} -> *{self.newname}*
    {self.description}
"""

class convineAdminChange(AdminChange):
    def __init__(self, date: datetime, admins: list, newAdminName: str, description: Union[str, None] = None):
        super().__init__(date, description)
        self.oldADs = admins
        parent_division = admins[0].parent
        self.newAD = AdminDivision(newAdminName, parent_division)

        super().log()

    def export(self):
        return self.newAD

    def __str__(self):
        return f"""
* convineAdminChange {self.ID}
  Date: {self.date}
    {",".join([ad.name for ad in self.oldADs])} -> *{self.newAD.name}*
    {self.description}
"""

class absorbAdminChange(AdminChange):
    def __init__(self, date: datetime, to_: AdminDivision, ob_: AdminDivision, description: Union[str, None] = None):
        super().__init__(date, description)
        ob_.status = "Deactivate"
        self.to = to_
        self.ob = ob_

        super().log()

    def __str__(self):
        return f"""
* absorbAdminChange {self.ID}
  Date: {self.date}
    *{self.to.name}* <-- {self.ob.name}
    {self.description}
"""

class separateAdminChange(AdminChange):
    def __init__(self, date: datetime, origin: AdminDivision, newAdminName: str, description: Union[str, None] = None):
        super().__init__(date, description)
        self.originAD = origin

        parent_division = origin.parent
        self.newAD = AdminDivision(newAdminName, parent_division)

        super().log()

    def export(self):
        return self.newAD

    def __str__(self):
        return f"""
* separateAdminChange {self.ID}
  Date: {self.date}
    {self.originAD.name} -> {self.originAD.name}, *{self.newAD.name}*
    {self.description}
"""

class divideAdminChange(AdminChange):
    def __init__(self, date: datetime, origin: AdminDivision, toNames: list, description: Union[str, None] = None):
        super().__init__(date, description)
        self.originAD = origin

        parent_division = origin.parent        
        self.toADs = [AdminDivision(newAdminName, parent_division) for newAdminName in toNames]

        super().log()

    def export(self):
        return self.toADs

    def __str__(self):
        return f"""
* divideAdminChange {self.ID}
  Date: {self.date}
    {self.originAD.name} -> *{"*,*".join([ad.name for ad in self.toADs])}*
    {self.description}
"""


JAPAN = newAdminChange(datetime(2023,1,1), "japan", description="hoge").export()
TOKYO = newAdminChange(datetime(2023,1,2), "tokyo", parent_division=JAPAN).export()
SAITAMA = newAdminChange(datetime(2023,1,2), "saitama", parent_division=JAPAN).export()
CAP = convineAdminChange(datetime(2023,2,2), [TOKYO, SAITAMA], "newTokyo").export()
SAITAMA = separateAdminChange(datetime(2023,2,2), CAP, "saitama").export()
nameAdminChange(datetime(2023,2,2), CAP, "tokyo")
divideAdminChange(datetime(2023,10,1), CAP, ["tokyo1", "tokyo2"])

for s in snap:
    print(s)
