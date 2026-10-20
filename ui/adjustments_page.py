from .movement_page import MovementPage


class AdjustmentsPage(MovementPage):
    def __init__(self,parent,context,on_changed):
        super().__init__(parent, context, on_changed, 'ADJUST')
