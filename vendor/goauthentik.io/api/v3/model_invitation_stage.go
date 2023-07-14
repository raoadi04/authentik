/*
authentik

Making authentication simple.

API version: 2023.6.1
Contact: hello@goauthentik.io
*/

// Code generated by OpenAPI Generator (https://openapi-generator.tech); DO NOT EDIT.

package api

import (
	"encoding/json"
)

// InvitationStage InvitationStage Serializer
type InvitationStage struct {
	Pk   string `json:"pk"`
	Name string `json:"name"`
	// Get object type so that we know how to edit the object
	Component string `json:"component"`
	// Return object's verbose_name
	VerboseName string `json:"verbose_name"`
	// Return object's plural verbose_name
	VerboseNamePlural string `json:"verbose_name_plural"`
	// Return internal model name
	MetaModelName string    `json:"meta_model_name"`
	FlowSet       []FlowSet `json:"flow_set,omitempty"`
	// If this flag is set, this Stage will jump to the next Stage when no Invitation is given. By default this Stage will cancel the Flow when no invitation is given.
	ContinueFlowWithoutInvitation *bool `json:"continue_flow_without_invitation,omitempty"`
}

// NewInvitationStage instantiates a new InvitationStage object
// This constructor will assign default values to properties that have it defined,
// and makes sure properties required by API are set, but the set of arguments
// will change when the set of required properties is changed
func NewInvitationStage(pk string, name string, component string, verboseName string, verboseNamePlural string, metaModelName string) *InvitationStage {
	this := InvitationStage{}
	this.Pk = pk
	this.Name = name
	this.Component = component
	this.VerboseName = verboseName
	this.VerboseNamePlural = verboseNamePlural
	this.MetaModelName = metaModelName
	return &this
}

// NewInvitationStageWithDefaults instantiates a new InvitationStage object
// This constructor will only assign default values to properties that have it defined,
// but it doesn't guarantee that properties required by API are set
func NewInvitationStageWithDefaults() *InvitationStage {
	this := InvitationStage{}
	return &this
}

// GetPk returns the Pk field value
func (o *InvitationStage) GetPk() string {
	if o == nil {
		var ret string
		return ret
	}

	return o.Pk
}

// GetPkOk returns a tuple with the Pk field value
// and a boolean to check if the value has been set.
func (o *InvitationStage) GetPkOk() (*string, bool) {
	if o == nil {
		return nil, false
	}
	return &o.Pk, true
}

// SetPk sets field value
func (o *InvitationStage) SetPk(v string) {
	o.Pk = v
}

// GetName returns the Name field value
func (o *InvitationStage) GetName() string {
	if o == nil {
		var ret string
		return ret
	}

	return o.Name
}

// GetNameOk returns a tuple with the Name field value
// and a boolean to check if the value has been set.
func (o *InvitationStage) GetNameOk() (*string, bool) {
	if o == nil {
		return nil, false
	}
	return &o.Name, true
}

// SetName sets field value
func (o *InvitationStage) SetName(v string) {
	o.Name = v
}

// GetComponent returns the Component field value
func (o *InvitationStage) GetComponent() string {
	if o == nil {
		var ret string
		return ret
	}

	return o.Component
}

// GetComponentOk returns a tuple with the Component field value
// and a boolean to check if the value has been set.
func (o *InvitationStage) GetComponentOk() (*string, bool) {
	if o == nil {
		return nil, false
	}
	return &o.Component, true
}

// SetComponent sets field value
func (o *InvitationStage) SetComponent(v string) {
	o.Component = v
}

// GetVerboseName returns the VerboseName field value
func (o *InvitationStage) GetVerboseName() string {
	if o == nil {
		var ret string
		return ret
	}

	return o.VerboseName
}

// GetVerboseNameOk returns a tuple with the VerboseName field value
// and a boolean to check if the value has been set.
func (o *InvitationStage) GetVerboseNameOk() (*string, bool) {
	if o == nil {
		return nil, false
	}
	return &o.VerboseName, true
}

// SetVerboseName sets field value
func (o *InvitationStage) SetVerboseName(v string) {
	o.VerboseName = v
}

// GetVerboseNamePlural returns the VerboseNamePlural field value
func (o *InvitationStage) GetVerboseNamePlural() string {
	if o == nil {
		var ret string
		return ret
	}

	return o.VerboseNamePlural
}

// GetVerboseNamePluralOk returns a tuple with the VerboseNamePlural field value
// and a boolean to check if the value has been set.
func (o *InvitationStage) GetVerboseNamePluralOk() (*string, bool) {
	if o == nil {
		return nil, false
	}
	return &o.VerboseNamePlural, true
}

// SetVerboseNamePlural sets field value
func (o *InvitationStage) SetVerboseNamePlural(v string) {
	o.VerboseNamePlural = v
}

// GetMetaModelName returns the MetaModelName field value
func (o *InvitationStage) GetMetaModelName() string {
	if o == nil {
		var ret string
		return ret
	}

	return o.MetaModelName
}

// GetMetaModelNameOk returns a tuple with the MetaModelName field value
// and a boolean to check if the value has been set.
func (o *InvitationStage) GetMetaModelNameOk() (*string, bool) {
	if o == nil {
		return nil, false
	}
	return &o.MetaModelName, true
}

// SetMetaModelName sets field value
func (o *InvitationStage) SetMetaModelName(v string) {
	o.MetaModelName = v
}

// GetFlowSet returns the FlowSet field value if set, zero value otherwise.
func (o *InvitationStage) GetFlowSet() []FlowSet {
	if o == nil || o.FlowSet == nil {
		var ret []FlowSet
		return ret
	}
	return o.FlowSet
}

// GetFlowSetOk returns a tuple with the FlowSet field value if set, nil otherwise
// and a boolean to check if the value has been set.
func (o *InvitationStage) GetFlowSetOk() ([]FlowSet, bool) {
	if o == nil || o.FlowSet == nil {
		return nil, false
	}
	return o.FlowSet, true
}

// HasFlowSet returns a boolean if a field has been set.
func (o *InvitationStage) HasFlowSet() bool {
	if o != nil && o.FlowSet != nil {
		return true
	}

	return false
}

// SetFlowSet gets a reference to the given []FlowSet and assigns it to the FlowSet field.
func (o *InvitationStage) SetFlowSet(v []FlowSet) {
	o.FlowSet = v
}

// GetContinueFlowWithoutInvitation returns the ContinueFlowWithoutInvitation field value if set, zero value otherwise.
func (o *InvitationStage) GetContinueFlowWithoutInvitation() bool {
	if o == nil || o.ContinueFlowWithoutInvitation == nil {
		var ret bool
		return ret
	}
	return *o.ContinueFlowWithoutInvitation
}

// GetContinueFlowWithoutInvitationOk returns a tuple with the ContinueFlowWithoutInvitation field value if set, nil otherwise
// and a boolean to check if the value has been set.
func (o *InvitationStage) GetContinueFlowWithoutInvitationOk() (*bool, bool) {
	if o == nil || o.ContinueFlowWithoutInvitation == nil {
		return nil, false
	}
	return o.ContinueFlowWithoutInvitation, true
}

// HasContinueFlowWithoutInvitation returns a boolean if a field has been set.
func (o *InvitationStage) HasContinueFlowWithoutInvitation() bool {
	if o != nil && o.ContinueFlowWithoutInvitation != nil {
		return true
	}

	return false
}

// SetContinueFlowWithoutInvitation gets a reference to the given bool and assigns it to the ContinueFlowWithoutInvitation field.
func (o *InvitationStage) SetContinueFlowWithoutInvitation(v bool) {
	o.ContinueFlowWithoutInvitation = &v
}

func (o InvitationStage) MarshalJSON() ([]byte, error) {
	toSerialize := map[string]interface{}{}
	if true {
		toSerialize["pk"] = o.Pk
	}
	if true {
		toSerialize["name"] = o.Name
	}
	if true {
		toSerialize["component"] = o.Component
	}
	if true {
		toSerialize["verbose_name"] = o.VerboseName
	}
	if true {
		toSerialize["verbose_name_plural"] = o.VerboseNamePlural
	}
	if true {
		toSerialize["meta_model_name"] = o.MetaModelName
	}
	if o.FlowSet != nil {
		toSerialize["flow_set"] = o.FlowSet
	}
	if o.ContinueFlowWithoutInvitation != nil {
		toSerialize["continue_flow_without_invitation"] = o.ContinueFlowWithoutInvitation
	}
	return json.Marshal(toSerialize)
}

type NullableInvitationStage struct {
	value *InvitationStage
	isSet bool
}

func (v NullableInvitationStage) Get() *InvitationStage {
	return v.value
}

func (v *NullableInvitationStage) Set(val *InvitationStage) {
	v.value = val
	v.isSet = true
}

func (v NullableInvitationStage) IsSet() bool {
	return v.isSet
}

func (v *NullableInvitationStage) Unset() {
	v.value = nil
	v.isSet = false
}

func NewNullableInvitationStage(val *InvitationStage) *NullableInvitationStage {
	return &NullableInvitationStage{value: val, isSet: true}
}

func (v NullableInvitationStage) MarshalJSON() ([]byte, error) {
	return json.Marshal(v.value)
}

func (v *NullableInvitationStage) UnmarshalJSON(src []byte) error {
	v.isSet = true
	return json.Unmarshal(src, &v.value)
}
