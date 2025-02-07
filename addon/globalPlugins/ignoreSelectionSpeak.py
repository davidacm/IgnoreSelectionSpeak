# -*- coding: UTF-8 -*-
# Personal utils: This add-on contains personal utils. Some crazy things too.
# Copyright (C) 2025 David CM
# Author: David CM <dhf360@gmail.com>
# Released under GPL 2
#globalPlugins/ignoreSelectionSpeak.py


import api
import treeInterceptorHandler
import textInfos
import speech
import speechDictHandler
import globalPluginHandler
import ui
import addonHandler
from scriptHandler import script
addonHandler.initTranslation()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	# Translators: script category for add-on gestures
	scriptCategory = _("Ignore Selection Speak")
	def __init__(self):
		super(globalPluginHandler.GlobalPlugin, self).__init__()
		self._addedStrings:list[speechDictHandler.SpeechDictEntry] = []

	@script(
			# Translators: Ignore Current Selection gesture description
			_("adds the current selected text to the temporary dictionary, replacing it by an empty string"),
			gesture="kb(laptop):nvda+alt+i")
	def script_IgnoreCurrentSelection(self, gesture):
		obj = api.getFocusObject()
		treeInterceptor = obj.treeInterceptor
		if (
			isinstance(treeInterceptor, treeInterceptorHandler.DocumentTreeInterceptor)
			and not treeInterceptor.passThrough
		):
			obj = treeInterceptor
		try:
			info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
		except (RuntimeError, NotImplementedError):
			info = None
		if not info or info.isCollapsed:
			# Translators: The message reported when there is no selection
			ui.message(_("No selection"))
		else:
			entry = speechDictHandler.SpeechDictEntry(info.text, "", "")
			# the announcement should happen before adding it to the dictionary. Otherwice the added string won't be spoken.
			# Translators: the selected string was added to the temporary dictionary.
			ui.message(_("%s added to temporary dictionary") % entry.pattern)
			speechDictHandler.dictionaries['temp'].append(entry)
			self._addedStrings.append(entry)


	@script(
			# Translators: remove last added string gesture description.
			_("this script removes the latest string added to the temporary dictionary by this add-on. So, if you add 3 strings and call this script 3 times, the last three strings will be removed in reverse order"),
			gesture="kb(laptop):nvda+alt+r")
	def script_removeLastAddedString(self, gesture):
		if not self._addedStrings:
			# Translators: No strings to remove, if the list of ignored strings is empty.
			ui.message(_("No strings to remove"))
			return
		entry = self._addedStrings.pop()
		for i,k in enumerate(speechDictHandler.dictionaries['temp'][::-1]):
			if entry == k:
				del speechDictHandler.dictionaries['temp'][-1-i]
				# Translators: the ignored string was removed from the temporary dictionary.
				ui.message(_("removed the string %s from temporary dictionary") % entry.pattern)
				return
		# Translators: error removing the string, because it was not found.
		ui.message(_("Error removing the last entry %s. This was not found in the temporary dictionary") % entry.pattern)
