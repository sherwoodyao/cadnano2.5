# -*- coding: utf-8 -*-
from datetime import datetime
FORMAT_VERSION = "3.0"

def encodeDocument(document):
  doc_dict = {'format': FORMAT_VERSION,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'name': "",
        'parts': [],
        'modifications': document.modifications()
  }
  parts_list = doc_dict['parts']
  for part in document.getParts():
      part_dict = encodePart(part)
      parts_list.append(part_dict)
  return doc_dict
# end def

def encodePart(part):
    """
    Args:
        part (Part):
    """
    number_of_helices = part.getIdNumMax()
    vh_insertions = part.insertions()

    # iterate through virtualhelix list
    group_props = part.getPropertyDict().copy()
    view_props = part.view_properties
    vh_props, origins = part.helixPropertiesAndOrigins()

    # group_props['total_id_nums'] =
    group_props['virtual_helices'] = vh_props
    group_props['origins'] = origins

    xover_list = []
    strand_list = []
    prop_list = []
    vh_list = []
    for id_num in range(number_of_helices + 1):
        offset_and_size = part.getOffsetAndSize(id_num)
        if offset_and_size is None:
            # add a placeholder
            strand_list.append(None)
            prop_list.append(None)
        else:
            offset, size = offset_and_size
            vh_list.append((id_num, size))
            fwd_ss, rev_ss = part.getStrandSets(id_num)
            fwd_idxs, fwd_colors  = fwd_ss.dump(xover_list)
            rev_idxs, rev_colors  = rev_ss.dump(xover_list)
            strand_list.append((fwd_idxs, rev_idxs))
            prop_list.append((fwd_colors, rev_colors))
    # end for
    group_props['vh_list'] = vh_list
    group_props['strands'] = {  'indices': strand_list,
                                'properties': prop_list
                            }
    group_props['insertions'] = list(part.dumpInsertions())
    group_props['xovers'] = xover_list
    # oligo_dict = {k: v for k, v in zip( oligo.ALL_KEYS,
    #                                 zip(o.dump() for o in part.oligos()))
    #             }
    group_props['oligos'] = [o.dump() for o in part.oligos()]
    group_props['view_properties'] = view_props
    group_props['uuid'] = part.uuid
    return group_props
# end def

def encodePart2(part, vh_group_list=None):
    """
    Args:
        part (Part):
        vh_group_list (List[int]): list of virtual_helices to encode to be used
            with copy and paste serialization
    """
    vh_group_list.sort()
    number_of_helices = part.getIdNumMax()
    vh_insertions = part.insertions()

    # iterate through virtualhelix list
    group_props = part.getPropertyDict().copy()
    vh_props, origins = part.helixPropertiesAndOrigins(vh_group_list)

    group_props['virtual_helices'] = vh_props
    group_props['origins'] = origins

    xover_list = []
    strand_list = []
    prop_list = []
    vh_list = []
    vh_group_set = set(vh_group_list)
    filter_xovers = lambda x: (  x[0] in vh_group_set and
                    x[3] in vh_group_set)
    filter_vh = lambda x: x[0] in vh_group_set
    for id_num in vh_group_list:
        offset_and_size = part.getOffsetAndSize(id_num)
        if offset_and_size is None:
            # add a placeholder
            # print("Whoops", id_num)
            strand_list.append(None)
            prop_list.append(None)
        else:
            offset, size = offset_and_size
            vh_list.append((id_num, size))
            fwd_ss, rev_ss = part.getStrandSets(id_num)
            fwd_idxs, fwd_colors = fwd_ss.dump(xover_list)
            rev_idxs, rev_colors = rev_ss.dump(xover_list)
            strand_list.append((fwd_idxs, rev_idxs))
            prop_list.append((fwd_colors, rev_colors))
    # end for

    remap = {x: y for x, y in zip(   vh_group_list,
                                    range(len(vh_group_list))
                                )}
    group_props['vh_list'] = vh_list
    group_props['strands'] = {  'indices': strand_list,
                                'properties': prop_list
                            }
    filtered_insertions = filter(filter_vh, part.dumpInsertions())
    group_props['insertions'] = [(remap[x], y, z) for x, y, z in filtered_insertions]

    filtered_xover_list = filter(filter_xovers, xover_list)
    group_props['xovers'] = [(remap[a], b, c, remap[x], y, z)
                                for a, b, c, x, y, z in filtered_xover_list]

    view_props = part.view_properties.copy()
    vh_order = filter(lambda x: x in vh_group_set, group_props['virtual_helix_order'])
    vh_order = [remap[x] for x in vh_order]
    group_props['virtual_helix_order'] = vh_order
    group_props['view_properties'] = view_props

    external_mods_instances = filter(filter_vh,
                                 part.dumpModInstances(is_internal=False))
    group_props['external_mod_instances'] = [(remap[w], x, y, z)
                            for w, x, y, z in external_mods_instances]
    """ TODO Add in Document modifications

    """
    return group_props
# end def