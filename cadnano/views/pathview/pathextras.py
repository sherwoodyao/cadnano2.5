# -*- coding: utf-8 -*-
"""Summary

Attributes:
    BASE_RECT (TYPE): Description
    BASE_WIDTH (TYPE): Description
    KEYINPUT_ACTIVE_FLAG (TYPE): Description
    PHOS_ITEM_WIDTH (TYPE): Description
    PROX_ALPHA (int): Description
    T180 (TYPE): Description
    TRIANGLE (TYPE): Description
"""
from math import floor

from PyQt5.QtCore import QRectF, Qt, QObject, QPointF
from PyQt5.QtCore import QPropertyAnimation, pyqtProperty
from PyQt5.QtGui import QBrush, QColor, QPainterPath
from PyQt5.QtGui import QPolygonF, QTransform
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsRectItem, QGraphicsItem
from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtWidgets import QGraphicsSimpleTextItem

from cadnano import util
from cadnano.proxies.cnenum import HandleType, StrandType
from cadnano.gui.palette import getNoPen, getPenObj, newPenObj
from cadnano.gui.palette import getBrushObj, getNoBrush
from cadnano.views.resizehandles import ResizeHandleGroup
from . import pathstyles as styles


BASE_WIDTH = styles.PATH_BASE_WIDTH
BASE_RECT = QRectF(0, 0, BASE_WIDTH, BASE_WIDTH)


PHOS_ITEM_WIDTH = 0.25*BASE_WIDTH
TRIANGLE = QPolygonF()
TRIANGLE.append(QPointF(0, 0))
TRIANGLE.append(QPointF(0.75 * PHOS_ITEM_WIDTH, 0.5 * PHOS_ITEM_WIDTH))
TRIANGLE.append(QPointF(0, PHOS_ITEM_WIDTH))
TRIANGLE.append(QPointF(0, 0))
TRIANGLE.translate(0, -0.5*PHOS_ITEM_WIDTH)
T180 = QTransform()
T180.rotate(-180)
FWDPHOS_PP, REVPHOS_PP = QPainterPath(), QPainterPath()
FWDPHOS_PP.addPolygon(TRIANGLE)
REVPHOS_PP.addPolygon(T180.map(TRIANGLE))

KEYINPUT_ACTIVE_FLAG = QGraphicsItem.ItemIsFocusable


class PropertyWrapperObject(QObject):
    """Summary

    Attributes:
        animations (dict): Description
        brush_alpha (TYPE): Description
        item (TYPE): Description
        rotation (TYPE): Description
    """

    def __init__(self, item):
        """Summary

        Args:
            item (TYPE): Description
        """
        super(PropertyWrapperObject, self).__init__()
        self.item = item
        self.animations = {}

    def __get_brushAlpha(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return self.item.brush().color().alpha()

    def __set_brushAlpha(self, alpha):
        """Summary

        Args:
            alpha (TYPE): Description

        Returns:
            TYPE: Description
        """
        brush = QBrush(self.item.brush())
        color = QColor(brush.color())
        color.setAlpha(alpha)
        self.item.setBrush(QBrush(color))

    def __get_rotation(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return self.item.rotation()

    def __set_rotation(self, angle):
        """Summary

        Args:
            angle (TYPE): Description

        Returns:
            TYPE: Description
        """
        self.item.setRotation(angle)

    def saveRef(self, property_name, animation):
        """Summary

        Args:
            property_name (TYPE): Description
            animation (TYPE): Description

        Returns:
            TYPE: Description
        """
        self.animations[property_name] = animation

    def getRef(self, property_name):
        """Summary

        Args:
            property_name (TYPE): Description

        Returns:
            TYPE: Description
        """
        return self.animations.get(property_name)

    def destroy(self):
        """Summary

        Returns:
            TYPE: Description
        """
        self.item = None
        self.animations = None
        self.deleteLater()

    def resetAnimations(self):
        """Summary

        Returns:
            TYPE: Description
        """
        for item in self.animations.values():
            item.stop()
            item.deleteLater()
            item = None
        self.animations = {}

    brush_alpha = pyqtProperty(int, __get_brushAlpha, __set_brushAlpha)
    rotation = pyqtProperty(float, __get_rotation, __set_rotation)
# end class


class Triangle(QGraphicsPathItem):
    """Summary

    Attributes:
        adapter (TYPE): Description
    """

    def __init__(self, painter_path, parent=None):
        """Summary

        Args:
            painter_path (TYPE): Description
            parent (None, optional): Description
        """
        super(QGraphicsPathItem, self).__init__(painter_path, parent)
        self.adapter = PropertyWrapperObject(self)
    # end def
# end class


class PreXoverLabel(QGraphicsSimpleTextItem):
    """Summary

    Attributes:
        is_fwd (TYPE): Description
    """
    _XO_FONT = styles.XOVER_LABEL_FONT
    _XO_BOLD = styles.XOVER_LABEL_FONT_BOLD
    _FM = QFontMetrics(_XO_FONT)

    def __init__(self, is_fwd, pre_xover_item):
        """Summary

        Args:
            is_fwd (TYPE): Description
            color (TYPE): Description
            pre_xover_item (TYPE): Description
        """
        super(QGraphicsSimpleTextItem, self).__init__(pre_xover_item)
        self.is_fwd = is_fwd
        self._tbr = None
        self._outline = QGraphicsRectItem(self)
        self.setFont(self._XO_FONT)
        self.setBrush(getBrushObj('#666666'))
    # end def

    def resetItem(self, is_fwd, color):
        """Summary

        Args:
            is_fwd (TYPE): Description
            color (TYPE): Description

        Returns:
            TYPE: Description
        """
        self.is_fwd = is_fwd
        self._color = color
    # end def

    def setTextAndStyle(self, text, outline=False):
        """Summary

        Args:
            text (TYPE): Description
            outline (bool, optional): Description

        Returns:
            TYPE: Description
        """
        str_txt = str(text)
        self._tbr = tBR = self._FM.tightBoundingRect(str_txt)
        half_label_H = tBR.height() / 2.0
        half_label_W = tBR.width() / 2.0

        labelX = BASE_WIDTH/2.0 - half_label_W
        if str_txt == '1':  # adjust for the number one
            labelX -= tBR.width()

        labelY = half_label_H if self.is_fwd else (BASE_WIDTH - tBR.height())/2

        self.setPos(labelX, labelY)
        self.setText(str_txt)

        if outline:
            self.setFont(self._XO_BOLD)
            self.setBrush(getBrushObj('#ff0000'))
        else:
            self.setFont(self._XO_FONT)
            self.setBrush(getBrushObj('#666666'))

        if outline:
            r = QRectF(self._tbr).adjusted(-half_label_W, 0,
                                           half_label_W, half_label_H)
            self._outline.setRect(r)
            self._outline.setPen(getPenObj('#ff0000', 0.25))
            self._outline.setY(2*half_label_H)
            self._outline.show()
        else:
            self._outline.hide()
    # end def
# end class


PROX_ALPHA = 64


def _createPreXoverPainterPath(p1, p2, p3, end_poly=None, is_fwd=True):
    path = QPainterPath()
    path.moveTo(p1)
    path.lineTo(p2)
    path.lineTo(p3)
    if end_poly:
        poly_width = end_poly.boundingRect().height()/2
        xoffset = -poly_width if is_fwd else poly_width
        angle = -90 if is_fwd else 90
        T = QTransform()
        T.translate(p3.x()+xoffset, p3.y())
        T.rotate(angle)
        path.addPolygon(T.map(end_poly))
    return path
# end def


def _createDualPreXoverPainterPath(p1, p2, p3, p4, p5, p6, end_poly=None, is_fwd=True):
    path = QPainterPath()
    path.moveTo(p1)
    path.lineTo(p2)
    path.lineTo(p3)
    path.moveTo(p4)
    path.lineTo(p5)
    path.lineTo(p6)
    if end_poly is not None:
        h = end_poly.boundingRect().height()/2
        xoffset = -h if is_fwd else h
        w = end_poly.boundingRect().width()
        yoffset = w if is_fwd else -w
        angle = -90 if is_fwd else 90
        T = QTransform()
        T.translate(p6.x()+xoffset, p6.y()+yoffset)
        T.rotate(angle)
        path.addPolygon(T.map(end_poly))
    return path
# end def


# create hash marks QPainterPaths only once
CENTER_X = BASE_RECT.center().x()
CENTER_Y = BASE_RECT.center().y()
LO_X = BASE_RECT.left()
HI_X = BASE_RECT.right()
BOT_Y = BASE_RECT.bottom()+BASE_WIDTH/5
TOP_Y = BASE_RECT.top()-BASE_WIDTH/5
WIDTH_X = BASE_WIDTH/3
HEIGHT_Y = BASE_WIDTH/3

FWD_L1 = QPointF(LO_X, BOT_Y)
FWD_L2 = QPointF(LO_X+WIDTH_X, BOT_Y)
FWD_L3 = QPointF(LO_X+WIDTH_X, BOT_Y-HEIGHT_Y)
FWD_H1 = QPointF(HI_X, BOT_Y)
FWD_H2 = QPointF(HI_X-WIDTH_X, BOT_Y)
FWD_H3 = QPointF(HI_X-WIDTH_X, BOT_Y-HEIGHT_Y)
REV_L1 = QPointF(LO_X, TOP_Y)
REV_L2 = QPointF(LO_X+WIDTH_X, TOP_Y)
REV_L3 = QPointF(LO_X+WIDTH_X, TOP_Y+HEIGHT_Y)
REV_H1 = QPointF(HI_X, TOP_Y)
REV_H2 = QPointF(HI_X-WIDTH_X, TOP_Y)
REV_H3 = QPointF(HI_X-WIDTH_X, TOP_Y+HEIGHT_Y)

END_3P_WIDTH = styles.PREXOVER_STROKE_WIDTH*2
END_3P = QPolygonF()
END_3P.append(QPointF(0, 0))
END_3P.append(QPointF(0.75 * END_3P_WIDTH, 0.5 * END_3P_WIDTH))
END_3P.append(QPointF(0, END_3P_WIDTH))
END_3P.append(QPointF(0, 0))

_FWD_LO_PATH = _createPreXoverPainterPath(FWD_L1, FWD_L2, FWD_L3, end_poly=END_3P, is_fwd=True)
_FWD_HI_PATH = _createPreXoverPainterPath(FWD_H1, FWD_H2, FWD_H3)
_REV_LO_PATH = _createPreXoverPainterPath(REV_L1, REV_L2, REV_L3)
_REV_HI_PATH = _createPreXoverPainterPath(REV_H1, REV_H2, REV_H3, end_poly=END_3P, is_fwd=False)
_FWD_DUAL_PATH = _createDualPreXoverPainterPath(FWD_H1, FWD_H2, FWD_H3,
                                                FWD_L1, FWD_L2, FWD_L3, end_poly=END_3P, is_fwd=True)
_REV_DUAL_PATH = _createDualPreXoverPainterPath(REV_H1, REV_H2, REV_H3,
                                                REV_L1, REV_L2, REV_L3, end_poly=END_3P, is_fwd=False)

EMPTY_COL = '#cccccc'


class PreXoverItem(QGraphicsRectItem):
    """A PreXoverItem exists between a single 'from' VirtualHelixItem index
    and zero or more 'to' VirtualHelixItem Indices

    Attributes:
        adapter (TYPE): Description
        idx (int): the base index within the virtual helix
        is_fwd (TYPE): Description
        prexoveritem_manager (TYPE): Description
        to_vh_id_num (TYPE): Description
    """

    def __init__(self, from_virtual_helix_item, is_fwd, from_index, nearby_idxs,
                 to_vh_id_num, prexoveritem_manager):
        """Summary

        Args:
            from_virtual_helix_item (cadnano.views.pathview.virtualhelixitem.VirtualHelixItem): Description
            is_fwd (TYPE): Description
            from_index (TYPE): Description
            to_vh_id_num (TYPE): Description
            prexoveritem_manager (TYPE): Description
        """
        super(QGraphicsRectItem, self).__init__(BASE_RECT, from_virtual_helix_item)
        self.adapter = PropertyWrapperObject(self)
        self._tick_marks = QGraphicsPathItem(self)
        self._bond_item = QGraphicsPathItem(self)
        self._bond_item.hide()

        self.p1 = p1 = QGraphicsEllipseItem(0, 0, 5, 5, self)
        self.p2 = p2 = QGraphicsEllipseItem(0, 0, 5, 5, self)
        self.c1 = c1 = QGraphicsEllipseItem(0, 0, 5, 5, self)
        self.c2 = c2 = QGraphicsEllipseItem(0, 0, 5, 5, self)
        p1.setBrush(getBrushObj('#007200'))
        p2.setBrush(getBrushObj('#cc0000'))
        c1.setBrush(getBrushObj('#0000cc'))
        c2.setBrush(getBrushObj('#cc00cc'))
        p1.setPen(getNoPen())
        p2.setPen(getNoPen())
        c1.setPen(getNoPen())
        c2.setPen(getNoPen())
        p1.hide()
        p2.hide()
        c1.hide()
        c2.hide()

        self._label = PreXoverLabel(is_fwd, self)
        self._path = QGraphicsPathItem()
        self.setPen(getNoPen())
        self.resetItem(from_virtual_helix_item, is_fwd, from_index, nearby_idxs, to_vh_id_num, prexoveritem_manager)
        self._color = self.getStrandColor()
    # end def

    def getStrandColor(self):
        part = self._model_vh.part()
        id_num = self._id_num
        idx = self.idx
        strand_type = StrandType.FWD if self.is_fwd else StrandType.REV
        if part.hasStrandAtIdx(id_num, idx)[strand_type]:
            strand = part.getStrand(self.is_fwd, id_num, idx)
            color = strand.getColor() if strand is not None else EMPTY_COL
        else:
            color = EMPTY_COL
        return color
    # end def

    def shutdown(self):
        """Summary

        Returns:
            TYPE: Description
        """
        self.setBrush(getBrushObj(self._color, alpha=0))
        self.to_vh_id_num = None
        self.adapter.resetAnimations()
        self.setAcceptHoverEvents(False)
        self.hide()
    # end def

    def setPathAppearance(self, from_virtual_helix_item):
            """
            Sets the PainterPath according to the index (low = Left, high = Right)
            and strand position (top = Up, bottom = Down).
            """
            idx = self.idx
            bpr = from_virtual_helix_item.getProperty('bases_per_repeat')
            is_low = idx+1 in self.nearby_idxs or (idx+1) % bpr in self.nearby_idxs
            is_high = idx-1 in self.nearby_idxs or (idx-1) % bpr in self.nearby_idxs
            strand_type = StrandType.FWD if self.is_fwd else StrandType.REV
            if is_low and is_high:
                print("dual xover")
                path = (_FWD_DUAL_PATH, _REV_DUAL_PATH)[strand_type]
            elif is_low:
                path = (_FWD_LO_PATH, _REV_LO_PATH)[strand_type]
                self.is3p = True if self.is_fwd else False
            elif is_high:
                path = (_FWD_HI_PATH, _REV_HI_PATH)[strand_type]
                self.is3p = False if self.is_fwd else True
            else:
                print("unpaired PreXoverItem at {}[{}]".format(self._id_num, self.idx), self.nearby_idxs)
                return False
            self._tick_marks.setPen(getPenObj(self._color, styles.PREXOVER_STROKE_WIDTH,
                                              capstyle=Qt.FlatCap, joinstyle=Qt.RoundJoin))
            self._tick_marks.setPath(path)
            self._tick_marks.show()
            return True
    # end def

    def resetItem(self, from_virtual_helix_item, is_fwd, from_index, nearby_idxs,
                  to_vh_id_num, prexoveritem_manager):
        """Update this pooled PreXoverItem with current info.
        Called by PreXoverManager.

        Args:
            from_virtual_helix_item (cadnano.views.pathview.virtualhelixitem.VirtualHelixItem): the associated vh_item
            is_fwd (bool): True if associated with fwd strand, False if rev strand
            from_index (int): idx of associated vh
            to_vh_id_num (int): id_num of the other vh
            prexoveritem_manager (cadnano.views.pathview.prexoermanager.PreXoverManager): the manager
        """
        self.setParentItem(from_virtual_helix_item)
        self.resetTransform()
        self._id_num = from_virtual_helix_item.idNum()
        self._model_vh = from_virtual_helix_item.cnModel()
        self.idx = from_index
        self.nearby_idxs = nearby_idxs
        self.is_fwd = is_fwd
        self._color = color = self.getStrandColor()
        self.is3p = None
        self.to_vh_id_num = to_vh_id_num
        self.prexoveritem_manager = prexoveritem_manager

        # todo: check here if xover present and disable
        result = self.setPathAppearance(from_virtual_helix_item)

        if result:
            self.setBrush(getNoBrush())
            if is_fwd:
                self.setPos(from_index*BASE_WIDTH, -BASE_WIDTH)
            else:
                self.setPos(from_index*BASE_WIDTH, 2*BASE_WIDTH)
            self.show()
            # label
            self._label_txt = lbt = None if to_vh_id_num is None else str(to_vh_id_num)
            self.setLabel(text=lbt)
            self._label.resetItem(is_fwd, color)

            # bond line
            bonditem = self._bond_item
            bonditem.setPen(getPenObj(color, styles.PREXOVER_STROKE_WIDTH))
            bonditem.hide()

    # end def

    def getInfo(self):
        """
        Returns:
            Tuple: (from_id_num, is_fwd, from_index, to_vh_id_num)
        """
        return (self._id_num, self.is_fwd, self.idx, self.to_vh_id_num)

    ### ACCESSORS ###
    def color(self):
        """The PreXoverItem's color, derived from the associated strand's oligo.

        Returns:
            str: color in hex code
        """
        return self._color

    def remove(self):
        """Removes animation adapter, label, bond_item, and this item from scene.
        """
        scene = self.scene()
        self.adapter.destroy()
        if scene:
            scene.removeItem(self._label)
            self._label = None
            scene.removeItem(self._bond_item)
            self._bond_item = None
            self.adapter.resetAnimations()
            self.adapter = None
            scene.removeItem(self)
    # end defS

    ### EVENT HANDLERS ###
    def hoverEnterEvent(self, event):
        """Only if enableActive(True) is called hover and key events disabled by default

        Args:
            event (QGraphicsSceneHoverEvent): the hover event
        """
        self.setFocus(Qt.MouseFocusReason)
        self.prexoveritem_manager.updateModelActiveBaseInfo(self.getInfo())
        self.setActiveHovered(True)
        status_string = "%d[%d]" % (self._id_num, self.idx)
        self.parentItem().window().statusBar().showMessage(status_string)
    # end def

    def hoverLeaveEvent(self, event):
        """Summary

        Args:
            event (QGraphicsSceneHoverEvent): the hover event

        Returns:
            TYPE: Description
        """
        self.prexoveritem_manager.updateModelActiveBaseInfo(None)
        self.setActiveHovered(False)
        self.clearFocus()
        self.parentItem().window().statusBar().showMessage("")
    # end def

    def mousePressEvent(self, event):
        print("clicked yo", self.idx)
        part = self._model_vh.part()
        if self.is3p:
            strand5p = part.getStrand(self.is_fwd, self._id_num, self.idx)
            strand3p = part.getStrand(not self.is_fwd, self.to_vh_id_num, self.idx)
        else:
            strand5p = part.getStrand(self.is_fwd, self.to_vh_id_num, self.idx)
            strand3p = part.getStrand(not self.is_fwd, self._id_num, self.idx)
        part.createXover(strand5p, self.idx, strand3p, self.idx)

        nkey = (self.to_vh_id_num, not self.is_fwd, self.idx)
        npxi = self.prexoveritem_manager.neighbor_prexover_items.get(nkey, None)
        if npxi:
            print("shutdown", nkey)
            npxi.shutdown()
        self.shutdown()
        # self.prexoveritem_manager.handlePreXoverClick(self)

    def keyPressEvent(self, event):
        """Summary

        Args:
            event (TYPE): Description

        Returns:
            TYPE: Description
        """
        self.prexoveritem_manager.handlePreXoverKeyPress(event.key())
    # end def

    ### PUBLIC SUPPORT METHODS ###
    def setLabel(self, text=None, outline=False):
        """Summary

        Args:
            text (None, optional): Description
            outline (bool, optional): Description

        Returns:
            TYPE: Description
        """
        if text:
            self._label.setTextAndStyle(text=text, outline=outline)
            self._label.show()
        else:
            self._label.hide()
    # end def

    def animate(self, item, property_name, duration, start_value, end_value):
        """Summary

        Args:
            item (TYPE): Description
            property_name (TYPE): Description
            duration (TYPE): Description
            start_value (TYPE): Description
            end_value (TYPE): Description

        Returns:
            TYPE: Description
        """
        b_name = property_name.encode('ascii')
        anim = item.adapter.getRef(property_name)
        if anim is None:
            anim = QPropertyAnimation(item.adapter, b_name)
            item.adapter.saveRef(property_name, anim)
        anim.setDuration(duration)
        anim.setStartValue(start_value)
        anim.setEndValue(end_value)
        anim.start()
    # end def

    def setActiveHovered(self, is_active):
        """Rotate phosphate Triangle if `self.to_vh_id_num` is not `None`

        Args:
            is_active (bool): whether or not the PreXoverItem is parented to the
                active VirtualHelixItem
        """
        pass
    # end def

    def enableActive(self, is_active, to_vh_id_num=None):
        """Call on PreXoverItems created on the active VirtualHelixItem

        Args:
            is_active (TYPE): Description
            to_vh_id_num (None, optional): Description
        """
        if is_active:
            self.to_vh_id_num = to_vh_id_num
            self.setAcceptHoverEvents(True)
            if to_vh_id_num is None:
                self.setLabel(text=None)
            else:
                self.setLabel(text=str(to_vh_id_num))
        else:
            self.setBrush(getNoBrush())
            self.setAcceptHoverEvents(False)

    def activateNeighbor(self, active_prexoveritem, shortcut=None):
        """
        Draws a cubic line starting from the neighbor pxi (self) back to the active pxi
        To be called with whatever the active_prexoveritem is for the parts `active_base`.

        Args:
            active_prexoveritem (TYPE): Description
            shortcut (None, optional): Description
        """
        p1 = self._tick_marks.scenePos()
        p2 = active_prexoveritem._tick_marks.scenePos()
        scale = 1

        deltax1 = -BASE_WIDTH*scale if self.is_fwd else BASE_WIDTH*scale
        deltay1 = -BASE_WIDTH*scale if self.is_fwd else BASE_WIDTH*scale
        deltax2 = BASE_WIDTH*scale if active_prexoveritem.is_fwd else -BASE_WIDTH*scale
        deltay2 = BASE_WIDTH*scale if active_prexoveritem.is_fwd else -BASE_WIDTH*scale
        # c1 = self._bond_item.mapFromScene(QPointF(p1.x(), p1.y() + delta1))
        # c2 = QPointF(p2.x(), p2.y() - delta2)

        c1 = self._bond_item.mapFromScene(QPointF(p1.x()+deltax1, p1.y()+deltay1))
        c2 = self._bond_item.mapFromScene(QPointF(p2.x()+deltax2, p2.y()+deltay2))

        # print("p1({},{}), c1({},{}), c2({},{}), p2({},{})".format(p1.x(), p1.y(),
        #                                                           c1.x(), c1.y(),
        #                                                           c2.x(), c2.y(),
        #                                                           p2.x(), p2.y()))
        # self.p1.setPos(self._bond_item.mapFromScene(p1))  # green
        # self.p2.setPos(self._bond_item.mapFromScene(p2))  # red
        # self.c1.setPos(c1)  # blue
        # self.c2.setPos(c2)  # magenta
        # self.p1.show()
        # self.p2.show()
        # self.c1.show()
        # self.c2.show()
        pp = QPainterPath()
        pp.moveTo(self._bond_item.mapFromScene(p1))
        pp.cubicTo(c1, c2, self._bond_item.mapFromScene(p2))
        self._bond_item.setPath(pp)
        self._bond_item.show()
        self.setLabel(text=shortcut, outline=True)
    # end def

    def deactivateNeighbor(self):
        """Summary

        Returns:
            TYPE: Description
        """
        if self.isVisible():
            self.p1.hide()
            self.p2.hide()
            self.c1.hide()
            self.c2.hide()
            self._bond_item.hide()
            self.setLabel(text=self._label_txt)
    # end def
# end class


class PathWorkplaneOutline(QGraphicsRectItem):
    def __init__(self, parent=None):
        super(PathWorkplaneOutline, self).__init__(parent)
        self.setPen(getNoPen())
        self._path = QGraphicsPathItem(self)
        self._path.setBrush(getNoBrush())
        self._path.setPen(newPenObj(styles.BLUE_STROKE, 0))
    # end def

    def updateAppearance(self):
        tl = self.rect().topLeft()
        tl1 = tl + QPointF(0, -BASE_WIDTH/2)
        tl2 = tl + QPointF(BASE_WIDTH/2, -BASE_WIDTH/2)
        bl = self.rect().bottomLeft()
        bl1 = bl + QPointF(0, BASE_WIDTH/2)
        bl2 = bl + QPointF(BASE_WIDTH/2, BASE_WIDTH/2)
        tr = self.rect().topRight()
        tr1 = tr + QPointF(0, -BASE_WIDTH/2)
        tr2 = tr + QPointF(-BASE_WIDTH/2, -BASE_WIDTH/2)
        br = self.rect().bottomRight()
        br1 = br + QPointF(0, BASE_WIDTH/2)
        br2 = br + QPointF(-BASE_WIDTH/2, BASE_WIDTH/2)
        pp = QPainterPath()
        pp.moveTo(tl2)
        pp.lineTo(tl1)
        pp.lineTo(bl1)
        pp.lineTo(bl2)
        pp.moveTo(tr2)
        pp.lineTo(tr1)
        pp.lineTo(br1)
        pp.lineTo(br2)
        self._path.setPath(pp)
    # end def
# end class


class PathWorkplaneItem(QGraphicsRectItem):
    """Draws the rectangle to indicate the current Workplane, i.e. the
    region of part bases affected by certain actions in other views."""
    _BOUNDING_RECT_PADDING = 0
    _HANDLE_SIZE = 6
    _MIN_WIDTH = 3

    def __init__(self, model_part, part_item):
        super(QGraphicsRectItem, self).__init__(BASE_RECT, part_item)
        # self.setAcceptHoverEvents(True)
        # self.setBrush(getNoBrush())
        self.setBrush(getBrushObj(styles.BLUE_FILL, alpha=12))
        self.setPen(getNoPen())

        self.setZValue(styles.ZWORKPLANE)

        self._model_part = model_part
        self._part_item = part_item
        self._idx_low, self._idx_high = model_part.getProperty('workplane_idxs')
        self._low_drag_bound = 0  # idx, not pos
        self._high_drag_bound = model_part.getProperty('max_vhelix_length')  # idx, not pos

        self.outline = PathWorkplaneOutline(self)
        self.resize_handle_group = ResizeHandleGroup(self.rect(), self._HANDLE_SIZE, styles.BLUE_STROKE,
                                                     True, HandleType.LEFT | HandleType.RIGHT, self)
        self.model_bounds_hint = m_b_h = QGraphicsRectItem(self)
        m_b_h.setBrush(getBrushObj(styles.BLUE_FILL, alpha=64))
        m_b_h.setPen(getNoPen())
        m_b_h.hide()
    # end def

    def getModelMinBounds(self, handle_type=None):
        """Resize bounds in form of Qt position, scaled from model."""
        # todo: fix bug preventing dragging in imported files
        if handle_type and handle_type & HandleType.LEFT:
            xTL = (self._idx_high-self._MIN_WIDTH)*BASE_WIDTH
            xBR = self._idx_high*BASE_WIDTH
        elif handle_type and handle_type & HandleType.RIGHT:
            xTL = (self._idx_low+self._MIN_WIDTH)*BASE_WIDTH
            xBR = (self._idx_low)*BASE_WIDTH
        else:  # default to HandleType.RIGHT behavior for all types
            print("no ht??")
            xTL = 0
            xBR = self._high_drag_bound*BASE_WIDTH
        yTL = self._part_item._vh_rect.top()
        yBR = self._part_item._vh_rect.bottom()-BASE_WIDTH*3
        return xTL, yTL, xBR, yBR
    # end def

    def setMovable(self, is_movable):
        # self.setFlag(QGraphicsItem.ItemIsMovable, is_movable)
        pass
    # end def

    def finishDrag(self):
        """Set the workplane size in the model"""
        pass
        # pos = self.pos()
        # position = pos.x(), pos.y()
        # view_name = self._viewroot.name
        # self._model_part.changeInstanceProperty(self._model_instance, view_name, 'position', position)
    # end def

    def reconfigureRect(self, top_left, bottom_right, finish=False):
        """Update the workplane rect to draw from top_left to bottom_right,
        snapping the x values to the nearest base width. Updates the outline
        and resize handles.

        Args:
            top_left (tuple): topLeft (x, y)
            bottom_right (tuple): bottomRight (x, y)

        Returns:
            QRectF: the new rect.
        """
        if top_left:
            xTL = max(top_left[0], self._low_drag_bound)
            xTL = xTL - (xTL % BASE_WIDTH)  # snap to nearest base
            self._idx_low = xTL/BASE_WIDTH
        else:
            xTL = self._idx_low*BASE_WIDTH

        if bottom_right:
            xBR = util.clamp(bottom_right[0],
                             (self._idx_low+self._MIN_WIDTH)*BASE_WIDTH,
                             (self._high_drag_bound)*BASE_WIDTH)
            xBR = xBR - (xBR % BASE_WIDTH)  # snap to nearest base
            self._idx_high = xBR/BASE_WIDTH
        else:
            xBR = self._idx_high*BASE_WIDTH

        yTL = self._part_item._vh_rect.top()
        yBR = self._part_item._vh_rect.bottom()-BASE_WIDTH*3

        self.setRect(QRectF(QPointF(xTL, yTL), QPointF(xBR, yBR)))
        self.outline.setRect(self.rect())
        self.outline.updateAppearance()
        self.resize_handle_group.alignHandles(self.rect())
        self._model_part.setProperty('workplane_idxs', (self._idx_low, self._idx_high), use_undostack=False)
        return self.rect()

    def setIdxs(self, new_idxs):
        if self._idx_low != new_idxs[0] or self._idx_high != new_idxs[1]:
            self._idx_low = new_idxs[0]
            self._idx_high = new_idxs[1]
            self.reconfigureRect((), ())

    def showModelMinBoundsHint(self, handle_type, show=True):
        m_b_h = self.model_bounds_hint
        if show:
            xTL, yTL, xBR, yBR = self.getModelMinBounds(handle_type)
            m_b_h.setRect(QRectF(QPointF(xTL, yTL), QPointF(xBR, yBR)))
            m_b_h.show()
        else:
            m_b_h.hide()
            self._part_item.update()  # m_b_h hangs around unless force repaint
    # end def

    def width(self):
        return self._idx_high - self._idx_low
    # end def

    ### EVENT HANDLERS ###
    def hoverEnterEvent(self, event):
        self._part_item.updateStatusBar("{}–{}".format(self._idx_low, self._idx_high))
        QGraphicsItem.hoverEnterEvent(self, event)
    # end def

    def hoverMoveEvent(self, event):
        QGraphicsItem.hoverMoveEvent(self, event)
    # end def

    def hoverLeaveEvent(self, event):
        self._part_item.updateStatusBar("")
        QGraphicsItem.hoverLeaveEvent(self, event)
    # end def

    def mousePressEvent(self, event):
        """
        Parses a mousePressEvent. Stores _move_idx and _offset_idx for
        future comparison.
        """
        # self.setCursor(Qt.ClosedHandCursor)
        # if event.button() != Qt.LeftButton:
        if event.modifiers() != Qt.ShiftModifier:
            event.ignore()
            QGraphicsItem.mousePressEvent(self, event)
            return

        self._start_idx_low = self._idx_low
        self._start_idx_high = self._idx_high
        self._delta = 0
        self._move_idx = int(floor((self.x()+event.pos().x()) / BASE_WIDTH))
        self._offset_idx = int(floor(event.pos().x()) / BASE_WIDTH)
        self._high_drag_bound = self._model_part.getProperty('max_vhelix_length') - self.width()
    # end def

    def mouseMoveEvent(self, event):
        delta = int(floor((self.x()+event.pos().x()) / BASE_WIDTH)) - self._offset_idx
        delta = util.clamp(delta,
                           self._low_drag_bound-self._start_idx_low,
                           self._high_drag_bound-self._start_idx_high+self.width())
        if self._delta != delta:
            self._idx_low = self._start_idx_low + delta
            self._idx_high = self._start_idx_high + delta
            self._delta = delta
            self.reconfigureRect((), ())
    # end def

    def mouseReleaseEvent(self, event):
        delta = int(floor((self.x()+event.pos().x()) / BASE_WIDTH)) - self._offset_idx
        delta = util.clamp(delta,
                           self._low_drag_bound-self._start_idx_low,
                           self._high_drag_bound-self._start_idx_high+self.width())
        if self._delta != delta:
            self._idx_low = self._start_idx_low + delta
            self._idx_high = self._start_idx_high + delta
            self._delta = delta
            self.reconfigureRect((), ())
        self._high_drag_bound = self._model_part.getProperty('max_vhelix_length')  # reset for handles
    # end def
