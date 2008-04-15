/***************************************************************************
 *                                                                         *
 *   copyright : (C) 2007 The University of Toronto                        *
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

#ifndef PLOTITEM_H
#define PLOTITEM_H

#include "viewitem.h"
#include "graphicsfactory.h"

#include <QHash>

#include "relation.h"
#include "plotrenderitem.h"
#include "plotiteminterface.h"
#include "plotdefines.h"
#include "plotmarkers.h"

namespace Kst {

class PlotItem : public ViewItem, public PlotItemInterface
{
  Q_OBJECT
  public:
    enum MajorTickMode {
      Coarse = 2,
      Normal = 5,
      Fine = 10,
      VeryFine = 15
    };

    PlotItem(View *parent);
    virtual ~PlotItem();

    virtual QString plotName() const; //from PlotItemInterface

    QList<PlotRenderItem*> renderItems() const;
    PlotRenderItem *renderItem(PlotRenderItem::RenderType type);

    virtual void save(QXmlStreamWriter &xml);

    virtual void paint(QPainter *painter);

    /* This is the rectangle of the PlotAxis and includes the axis labels. */
    QRectF plotAxisRect() const;

    /* This is the rectangle of the PlotRenderItem's and includes the actual curves. */
    QRectF plotRect() const;

    /* This is the rectangle containing the union of all the PlotRenderItem's projections. */
    QRectF projectionRect() const;

    bool isTiedZoom() const;
    void setTiedZoom(bool tiedZoom);

    qreal leftLabelMargin() const;
    qreal rightLabelMargin() const;
    qreal topLabelMargin() const;
    qreal bottomLabelMargin() const;

    QString leftLabel() const;
    QString bottomLabel() const;
    QString rightLabel() const;
    QString topLabel() const;

    void setTopSuppressed(bool suppressed);
    void setBottomSuppressed(bool suppressed);
    void setLeftSuppressed(bool suppressed);
    void setRightSuppressed(bool suppressed);

    bool isBottomAxisVisible() const;
    void setBottomAxisVisible(bool visible);

    bool isLeftAxisVisible() const;
    void setLeftAxisVisible(bool visible);

    bool isLeftLabelVisible() const;
    void setLeftLabelVisible(bool visible);

    bool isBottomLabelVisible() const;
    void setBottomLabelVisible(bool visible);

    bool isRightLabelVisible() const;
    void setRightLabelVisible(bool visible);

    bool isTopLabelVisible() const;
    void setTopLabelVisible(bool visible);

    void setLabelsVisible(bool visible);

    qreal axisMarginWidth() const;
    qreal axisMarginHeight() const;

    MajorTickMode xAxisMajorTickMode() const;
    void setXAxisMajorTickMode(MajorTickMode mode);

    MajorTickMode yAxisMajorTickMode() const;
    void setYAxisMajorTickMode(MajorTickMode mode);

    int xAxisMinorTickCount() const;
    void setXAxisMinorTickCount(const int count);

    int yAxisMinorTickCount() const;
    void setYAxisMinorTickCount(const int count);

    bool drawXAxisMajorTicks() const;
    void setDrawXAxisMajorTicks(const bool draw);

    bool drawXAxisMinorTicks() const;
    void setDrawXAxisMinorTicks(const bool draw);

    bool drawYAxisMajorTicks() const;
    void setDrawYAxisMajorTicks(const bool draw);

    bool drawYAxisMinorTicks() const;
    void setDrawYAxisMinorTicks(const bool draw);

    bool drawXAxisMajorGridLines() const;
    void setDrawXAxisMajorGridLines(const bool draw);

    bool drawXAxisMinorGridLines() const;
    void setDrawXAxisMinorGridLines(const bool draw);

    bool drawYAxisMajorGridLines() const;
    void setDrawYAxisMajorGridLines(const bool draw);

    bool drawYAxisMinorGridLines() const;
    void setDrawYAxisMinorGridLines(const bool draw);

    QColor xAxisMajorGridLineColor() const;
    void setXAxisMajorGridLineColor(const QColor &color);

    QColor xAxisMinorGridLineColor() const;
    void setXAxisMinorGridLineColor(const QColor &color);

    QColor yAxisMajorGridLineColor() const;
    void setYAxisMajorGridLineColor(const QColor &color);

    QColor yAxisMinorGridLineColor() const;
    void setYAxisMinorGridLineColor(const QColor &color);

    Qt::PenStyle xAxisMajorGridLineStyle() const;
    void setXAxisMajorGridLineStyle(const Qt::PenStyle style);

    Qt::PenStyle xAxisMinorGridLineStyle() const;
    void setXAxisMinorGridLineStyle(const Qt::PenStyle style);

    Qt::PenStyle yAxisMajorGridLineStyle() const;
    void setYAxisMajorGridLineStyle(const Qt::PenStyle style);

    Qt::PenStyle yAxisMinorGridLineStyle() const;
    void setYAxisMinorGridLineStyle(const Qt::PenStyle style);

    int xAxisSignificantDigits() const;
    void setXAxisSignificantDigits(const int digits);

    int yAxisSignificantDigits() const;
    void setYAxisSignificantDigits(const int digits);

    QString bottomLabelOverride() const;
    void setBottomLabelOverride(const QString &label);

    QString leftLabelOverride() const;
    void setLeftLabelOverride(const QString &label);

    QString topLabelOverride() const;
    void setTopLabelOverride(const QString &label);

    QString rightLabelOverride() const;
    void setRightLabelOverride(const QString &label);

    QString titleOverride() const;
    void setTitleOverride(const QString &label);

    QFont topLabelFont() const;
    void setTopLabelFont(const QFont &font);

    QFont leftLabelFont() const;
    void setLeftLabelFont(const QFont &font);

    QFont rightLabelFont() const;
    void setRightLabelFont(const QFont &font);

    QFont bottomLabelFont() const;
    void setBottomLabelFont(const QFont &font);

    qreal bottomLabelFontScale() const;
    void setBottomLabelFontScale(const qreal scale);

    qreal leftLabelFontScale() const;
    void setLeftLabelFontScale(const qreal scale);

    qreal topLabelFontScale() const;
    void setTopLabelFontScale(const qreal scale);

    qreal rightLabelFontScale() const;
    void setRightLabelFontScale(const qreal scale);

    bool xAxisLog() const;
    void setXAxisLog(bool log);

    bool yAxisLog() const;
    void setYAxisLog(bool log);

    bool xAxisReversed() const;
    void setXAxisReversed(const bool enabled);

    bool yAxisReversed() const;
    void setYAxisReversed(const bool enabled);

    bool xAxisBaseOffset() const;
    void setXAxisBaseOffset(const bool enabled);

    bool yAxisBaseOffset() const;
    void setYAxisBaseOffset(const bool enabled);

    bool xAxisInterpret() const;
    void setXAxisInterpret(const bool enabled);

    bool yAxisInterpret() const;
    void setYAxisInterpret(const bool enabled);

    KstAxisDisplay xAxisDisplay() const;
    void setXAxisDisplay(const KstAxisDisplay display);

    KstAxisDisplay yAxisDisplay() const;
    void setYAxisDisplay(const KstAxisDisplay display);

    KstAxisInterpretation xAxisInterpretation() const;
    void setXAxisInterpretation(const KstAxisInterpretation interpret);

    KstAxisInterpretation yAxisInterpretation() const;
    void setYAxisInterpretation(const KstAxisInterpretation interpret);

    PlotMarkers xAxisPlotMarkers() { return _xAxisPlotMarkers; }
    void setXAxisPlotMarkers(const PlotMarkers &plotMarkers) { _xAxisPlotMarkers = plotMarkers; }

    PlotMarkers yAxisPlotMarkers() { return _yAxisPlotMarkers; }
    void setYAxisPlotMarkers(const PlotMarkers &plotMarkers) { _yAxisPlotMarkers = plotMarkers; }

    qreal mapXToPlot(const qreal &x) const;
    qreal mapYToPlot(const qreal &y) const;
    QPointF mapToPlot(const QPointF &point) const;

    QPointF mapToProjection(const QPointF &point);
    QRectF mapToProjection(const QRectF &rect);

    void updateScale();

    qreal xMin() { return _xMin; }
    qreal xMax() { return _xMax; }
    qreal yMin() { return _yMin; }
    qreal yMax() { return _yMax; }

    void triggerUpdate() { emit geometryChanged(); update(rect()); }

  Q_SIGNALS:
    void projectionRectChanged();
    void marginsChanged();
    void updatePlotRect();

  public Q_SLOTS:
    virtual void edit();

  private:
    virtual void paintPlot(QPainter *painter,
                                     const QList<qreal> &xMajorTicks,
                                     const QList<qreal> &xMinorTicks,
                                     const QList<qreal> &yMajorTicks,
                                     const QList<qreal> &yMinorTicks);

    virtual void paintMajorGridLines(QPainter *painter,
                                     const QList<qreal> &xMajorTicks,
                                     const QList<qreal> &yMajorTicks);

     virtual void paintMinorGridLines(QPainter *painter,
                                     const QList<qreal> &xMinorTicks,
                                     const QList<qreal> &yMinorTicks);

    virtual void paintMajorTicks(QPainter *painter,
                                 const QList<qreal> &xMajorTicks,
                                 const QList<qreal> &yMajorTicks);

    virtual void paintMinorTicks(QPainter *painter,
                                 const QList<qreal> &xMinorTicks,
                                 const QList<qreal> &yMinorTicks);

    virtual void paintTickLabels(QPainter *painter,
                                      const QList<qreal> &xMajorTicks,
                                      const QList<qreal> &yMajorTicks,
                                      const QMap<qreal, QString> &xLabels,
                                      const QMap<qreal, QString> &yLabels);

    virtual void paintBottomTickLabels(QPainter *painter,
                                      const QList<qreal> &xMajorTicks,
                                      const QMap<qreal, QString> &xLabels);

    virtual void paintLeftTickLabels(QPainter *painter,
                                      const QList<qreal> &yMajorTicks,
                                      const QMap<qreal, QString> &yLabels);

    virtual void paintPlotMarkers(QPainter *painter);

    qreal calculatedLabelMarginWidth() const;
    qreal calculatedLabelMarginHeight() const;

    qreal calculatedLeftLabelMargin() const;
    void setCalculatedLeftLabelMargin(qreal margin);

    qreal calculatedRightLabelMargin() const;
    void setCalculatedRightLabelMargin(qreal margin);

    qreal calculatedTopLabelMargin() const;
    void setCalculatedTopLabelMargin(qreal margin);

    qreal calculatedBottomLabelMargin() const;
    void setCalculatedBottomLabelMargin(qreal margin);

    QString interpretLabel(KstAxisInterpretation axisInterpretation, KstAxisDisplay axisDisplay, double base, double lastValue);
    double convertTimeValueToJD(KstAxisInterpretation axisInterpretation, double valueIn);
    QString convertJDToDateString(KstAxisInterpretation axisInterpretation, KstAxisDisplay axisDisplay, double dJD);
    double convertTimeDiffValueToDays(KstAxisInterpretation axisInterpretation, double offsetIn);
    double interpretOffset(KstAxisInterpretation axisInterpretation, KstAxisDisplay axisDisplay, double base, double value);

    QRectF topLabelRect(bool calc) const;
    QRectF bottomLabelRect(bool calc) const;
    QRectF leftLabelRect(bool calc) const;
    QRectF rightLabelRect(bool calc) const;

    void paintLeftLabel(QPainter *painter);
    QSizeF calculateLeftLabelBound(QPainter *painter);
    void paintBottomLabel(QPainter *painter);
    QSizeF calculateBottomLabelBound(QPainter *painter);
    void paintRightLabel(QPainter *painter);
    QSizeF calculateRightLabelBound(QPainter *painter);
    void paintTopLabel(QPainter *painter);
    QSizeF calculateTopLabelBound(QPainter *painter);

    QFont calculatedTopLabelFont();
    QFont calculatedBottomLabelFont();
    QFont calculatedLeftLabelFont();
    QFont calculatedRightLabelFont();

    qreal calculatedAxisMarginWidth() const;
    void setCalculatedAxisMarginWidth(qreal marginWidth);

    qreal calculatedAxisMarginHeight() const;
    void setCalculatedAxisMarginHeight(qreal marginHeight);

    void computeTicks(QList<qreal> *xMajorTicks, QList<qreal> *xMinorTicks, QList<qreal> *yMajorTicks, QList<qreal> *yMinorTicks, QMap<qreal, QString> *xLabels, QMap<qreal, QString> *yLabels);
    qreal computedMajorTickSpacing(Qt::Orientation orientation) const;
    void computeLogTicks(QList<qreal> *MajorTicks, QList<qreal> *MinorTicks, QMap<qreal, QString> *Labels, qreal min, qreal max, MajorTickMode tickMode);

    QSizeF calculateXTickLabelBound(QPainter *painter, const QList<qreal> &xMajorTicks);
    QSizeF calculateYTickLabelBound(QPainter *painter, const QList<qreal> &yMajorTicks);

  private Q_SLOTS:
    void calculateProjectionRect();

  private:
    QHash<PlotRenderItem::RenderType, PlotRenderItem*> _renderers;
    bool _isTiedZoom;
    bool _isLeftLabelVisible;
    bool _isBottomLabelVisible;
    bool _isRightLabelVisible;
    bool _isTopLabelVisible;
    bool _isBottomAxisVisible;
    bool _isLeftAxisVisible;
    qreal _calculatedLeftLabelMargin;
    qreal _calculatedRightLabelMargin;
    qreal _calculatedTopLabelMargin;
    qreal _calculatedBottomLabelMargin;
    qreal _calculatedLabelMarginWidth;
    qreal _calculatedLabelMarginHeight;
    qreal _calculatedAxisMarginWidth;
    qreal _calculatedAxisMarginHeight;

    QRectF _projectionRect;

    qreal _xMax;
    qreal _xMin;
    qreal _yMax;
    qreal _yMin;

    QRectF _yLabelRect;
    QRectF _xLabelRect;
    QString _leftLabelOverride;
    QString _bottomLabelOverride;
    QString _topLabelOverride;
    QString _rightLabelOverride;

    QFont _leftLabelFont;
    QFont _bottomLabelFont;
    QFont _topLabelFont;
    QFont _rightLabelFont;

    qreal _leftLabelFontScale;
    qreal _bottomLabelFontScale;
    qreal _topLabelFontScale;
    qreal _rightLabelFontScale;

    bool _xAxisLog;
    bool _yAxisLog;
    bool _xAxisReversed;
    bool _yAxisReversed;
    bool _xAxisBaseOffset;
    bool _yAxisBaseOffset;
    bool _xAxisInterpret;
    bool _yAxisInterpret;
    KstAxisDisplay _xAxisDisplay;
    KstAxisDisplay _yAxisDisplay;
    KstAxisInterpretation _xAxisInterpretation;
    KstAxisInterpretation _yAxisInterpretation;

    MajorTickMode _xAxisMajorTickMode;
    MajorTickMode _yAxisMajorTickMode;
    int _xAxisMinorTickCount;
    int _yAxisMinorTickCount;

    int _xAxisSignificantDigits;
    int _yAxisSignificantDigits;

    bool _drawXAxisMajorTicks;
    bool _drawXAxisMinorTicks;
    bool _drawYAxisMajorTicks;
    bool _drawYAxisMinorTicks;
    bool _drawXAxisMajorGridLines;
    bool _drawXAxisMinorGridLines;
    bool _drawYAxisMajorGridLines;
    bool _drawYAxisMinorGridLines;

    QColor _xAxisMajorGridLineColor;
    QColor _xAxisMinorGridLineColor;
    QColor _yAxisMajorGridLineColor;
    QColor _yAxisMinorGridLineColor;

    Qt::PenStyle _xAxisMajorGridLineStyle;
    Qt::PenStyle _xAxisMinorGridLineStyle;
    Qt::PenStyle _yAxisMajorGridLineStyle;
    Qt::PenStyle _yAxisMinorGridLineStyle;

    PlotMarkers _xAxisPlotMarkers;
    PlotMarkers _yAxisPlotMarkers;

    friend class ViewGridLayout;
};

class KST_EXPORT CreatePlotCommand : public CreateCommand
{
  public:
    CreatePlotCommand() : CreateCommand(QObject::tr("Create Plot")) {}
    CreatePlotCommand(View *view) : CreateCommand(view, QObject::tr("Create Plot")) {}
    virtual ~CreatePlotCommand() {}
    virtual void createItem();
};

class KST_EXPORT CreatePlotForCurve : public CreateCommand
{
  public:
    CreatePlotForCurve(bool createLayout, bool appendToLayout)
      : CreateCommand(QObject::tr("Create Plot For Curve")),
        _createLayout(createLayout),
        _appendToLayout(appendToLayout) {}
    CreatePlotForCurve(bool createLayout, bool appendToLayout, View *view)
      : CreateCommand(view, QObject::tr("Create Plot For Curve")),
        _createLayout(createLayout),
        _appendToLayout(appendToLayout) {}
    virtual ~CreatePlotForCurve() {}
    virtual void createItem();

  private:
    bool _createLayout;
    bool _appendToLayout;
};

class PlotItemFactory : public GraphicsFactory {
  public:
    PlotItemFactory();
    ~PlotItemFactory();
    ViewItem* generateGraphics(QXmlStreamReader& stream, ObjectStore *store, View *view, ViewItem *parent = 0);
};

}

#endif

// vim: ts=2 sw=2 et
