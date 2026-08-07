# src.utils.f1_calendar:RaceInfo
class, src/utils/f1_calendar.py:21, 13 lines

```python
@dataclass
class RaceInfo
```

Information about an F1 race weekend.

```python
season: int
race_number: int
gp_name: str
circuit_name: str
country: str
race_date: datetime
quali_date: Optional[datetime]
fp1_date: Optional[datetime]
fp2_date: Optional[datetime]
fp3_date: Optional[datetime]
is_sprint_weekend: bool
```

reads stdlib: datetime.datetime x5, typing.Optional x4, builtins.str x3, builtins.int x2, builtins.bool
writes internal: RaceInfo.circuit_name, RaceInfo.country, RaceInfo.fp1_date, RaceInfo.fp2_date, RaceInfo.fp3_date, RaceInfo.gp_name, RaceInfo.is_sprint_weekend, RaceInfo.quali_date, RaceInfo.race_date, RaceInfo.race_number, RaceInfo.season

referenced by: 15 sites, this module only
