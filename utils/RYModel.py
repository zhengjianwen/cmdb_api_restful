'''
Created on Aug 16, 2014
Enable a DJango database object to be modified by a data form or batch process
and only save to disk when data was actually changed.
Based on http://stackoverflow.com/a/13842223
Improvements:
* removed python 2 compatibility to simplify code
* proper handling of floating point
@author: Stanley@stanleyknutson.com
'''
from django.forms.models import model_to_dict
from django.db import models
from decimal import Decimal
    
class ModelDiffMixin(models.Model):
    """
    A model mixin that tracks model fields' values and provide useful API
    to know what fields have been changed.
    
    The main value is to allow simply changing the values and then saving the
    object only if it is "really changed"
    
    
    
    """

    def __init__(self, *args, **kwargs):
        super(ModelDiffMixin, self).__init__(*args, **kwargs)
        self.__initial = self._dict

    @property
    def diff(self):
        d1 = self.__initial
        d2 = self._dict
        # original version did not deal with floating point rounding (decimal(9,6) in database)
        #  diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        diffs = {}
        for k,v1 in d1.items() :
            v2 = d2[k]
            if isinstance(v1, Decimal) :
                v1 = float(v1)
            if isinstance(v2, Decimal) :
                v2  = float(v2)
            elif isinstance (v2, float) or isinstance(v1, float):
                # CAUTION: we assume the field is stored in db with 5 or more digits of precision
                # should really get the field definition and find the number of digits
                change = self.is_float_changed (v1, v2)
            else :
                change = v1 != v2
            if change : 
                diffs[k] = (v1, v2)
        
        return dict(diffs)
    
    def is_float_changed (self,v1, v2):
        ''' Compare two floating point or decimal values to the proper precision
        Default precision is 5 digits
        Override this method if all fload/decimal fields have fewer digits in database
        '''
        return abs (round (v1 - v2, 5)) > 0.00001

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.keys()

    def get_field_diff(self, field_name):
        """
        Returns a diff for field if it's changed and None otherwise.
        """
        return self.diff.get(field_name, None)

    def save(self, *args, **kwargs):
        """
        Saves model and set initial state.
        """
        super(ModelDiffMixin, self).save(*args, **kwargs)
        self.__initial = self._dict

    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in
                             self._meta.fields])

    class Meta:
        abstract = True
