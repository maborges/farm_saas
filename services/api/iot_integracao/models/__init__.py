"""Models para iot_integracao."""

from .john_deere import JohnDeere
from .case_ih import CaseIh
from .whatsapp import Whatsapp
from .comparador_precos import ComparadorPrecos

__all__ = ["JohnDeere", "CaseIh", "Whatsapp", "ComparadorPrecos"]
