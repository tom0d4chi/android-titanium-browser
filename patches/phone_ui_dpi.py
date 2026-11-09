#!/usr/bin/env python3
"""Phone interface switch, part 2: make Android pick the phone (non -sw600dp)
resources too, otherwise phone code runs against tablet layouts and crashes.
Run from chromium/src."""
import sys
DU = "ui/android/java/src/org/chromium/ui/display/DisplayUtil.java"
s = open(DU, encoding="utf-8").read()
old = ("    public static int getCurrentSmallestScreenWidth(Context context) {\n"
       "        if (sSmallestScreenWidthForTesting != null) {\n"
       "            return sSmallestScreenWidthForTesting;\n"
       "        }\n")
new = old + ("        try {\n"
             "            if (ContextUtils.getAppSharedPreferences().getBoolean(\"titanium_phone_ui\", false)) {\n"
             "                return 411;\n"
             "            }\n"
             "        } catch (Throwable t) {\n"
             "        }\n")
if s.count(old) != 1:
    sys.exit("phone_ui_dpi: anchor not found exactly once")
open(DU, "w", encoding="utf-8").write(s.replace(old, new))
print("phone_ui_dpi: OK")
