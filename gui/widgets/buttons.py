# File: gui/widgets/buttons.py

from PyQt5.QtWidgets import QToolButton, QMenu, QAction

class SplitButton(QToolButton):
    """
    A custom QToolButton that functions as a split button with a default action and a dropdown menu.
    """
    def __init__(self, text, tooltip, default_action, menu_actions, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setToolTip(tooltip)
        self.setPopupMode(QToolButton.MenuButtonPopup)
        self.clicked.connect(default_action)

        menu = QMenu(self)
        for action_text, action_callback in menu_actions:
            action = QAction(action_text, self)
            action.triggered.connect(action_callback)
            menu.addAction(action)
        self.setMenu(menu)
