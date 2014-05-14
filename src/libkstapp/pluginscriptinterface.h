/***************************************************************************
 *                                                                         *
 *   copyright : (C) 2012 C. Barth Netterfield                             *
 *                   netterfield@astro.utoronto.ca                         *
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

#include <QByteArray>
#include <QString>
#include <QSizeF>
#include <QList>

#include "scriptinterface.h"
#include "basicplugin.h"
#include "objectstore.h"

#ifndef PLUGINSCRIPTINTERFACE_H
#define PLUGINSCRIPTINTERFACE_H

namespace Kst {

class PluginSI : public ScriptInterface
{    
    Q_OBJECT
public:
    explicit PluginSI(BasicPluginPtr plugin);
    QString doCommand(QString);
    bool isValid();
    QByteArray endEditUpdate();

    static ScriptInterface* newPlugin(ObjectStore *store, QByteArray pluginName);
  private:
    BasicPluginPtr _plugin;
};


}
#endif // PLUGINSCRIPTINTERFACE_H
